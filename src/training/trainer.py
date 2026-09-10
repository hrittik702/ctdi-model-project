"""Training and validation loop for neural imputation models."""

import os
import time
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from typing import Dict, Any, Optional, Tuple
from src.training.losses import MaskedImputationLoss
from src.data.masking import generate_artificial_mask

try:
    from torch.utils.tensorboard import SummaryWriter
except ImportError:
    SummaryWriter = None

class PollutionImputationDataset(Dataset):
    """
    Dataset packaging 14-channel input data (9 context + 5 pollutants),
    pollutant observation mask, ground truth, and evaluation mask.
    Supports high-speed vectorized dynamic masking per epoch to prevent overfitting.
    """
    def __init__(
        self,
        x_all: np.ndarray,
        m_obs: np.ndarray,
        num_pollutants: int = 5,
        dynamic_masking: bool = False,
        fixed_m_art: Optional[np.ndarray] = None,
        fixed_eval_mask: Optional[np.ndarray] = None,
        missing_rate: float = 0.30
    ):
        self.x_all = np.nan_to_num(x_all, nan=0.0).astype(np.float32)
        self.m_obs = m_obs.astype(np.float32)
        self.num_pollutants = num_pollutants
        self.dynamic_masking = dynamic_masking
        self.missing_rate = missing_rate
        
        # Pollutants are the last num_pollutants channels
        self.pollutants_true = self.x_all[:, :, -num_pollutants:].copy()
        
        if not dynamic_masking:
            assert fixed_m_art is not None and fixed_eval_mask is not None, \
                "fixed_m_art and fixed_eval_mask required when dynamic_masking=False"
            self.m_art = fixed_m_art.astype(np.float32)
            self.eval_mask = fixed_eval_mask.astype(np.float32)
            
            # Prepare pre-masked inputs
            self.x_prepared = self.x_all.copy()
            p_masked = np.where(self.m_art == 1.0, self.pollutants_true, 0.0)
            self.x_prepared[:, :, -num_pollutants:] = p_masked
        else:
            self.regenerate_epoch_masks()
            
    def regenerate_epoch_masks(self):
        """Vectorized generation of dynamic artificial missingness masks in ~50ms."""
        N = len(self.x_all)
        rates = np.random.uniform(0.15, 0.40, size=(N, 1, 1)).astype(np.float32)
        rand_draw = np.random.rand(N, 24, self.num_pollutants).astype(np.float32)
        m_art = self.m_obs.copy()
        art_hidden = (rand_draw < rates) & (self.m_obs == 1.0)
        m_art[art_hidden] = 0.0
        
        # Add random missing contiguous blocks (2-6h) for ~35% of samples
        block_mask = np.random.rand(N, 1, self.num_pollutants) < 0.35
        starts = np.random.randint(0, 19, size=(N, 1, self.num_pollutants))
        lens = np.random.randint(2, 7, size=(N, 1, self.num_pollutants))
        time_indices = np.arange(24).reshape(1, 24, 1)
        in_block = (time_indices >= starts) & (time_indices < (starts + lens)) & block_mask
        m_art[in_block & (self.m_obs == 1.0)] = 0.0
        
        self.m_art = m_art.astype(np.float32)
        self.eval_mask = ((self.m_obs == 1.0) & (self.m_art == 0.0)).astype(np.float32)
        
        # Pre-mask pollutants in input tensor
        self.x_prepared = self.x_all.copy()
        p_masked = np.where(self.m_art == 1.0, self.pollutants_true, 0.0)
        self.x_prepared[:, :, -self.num_pollutants:] = p_masked

    def __len__(self) -> int:
        return len(self.x_all)
        
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        return (
            torch.from_numpy(self.x_prepared[idx]),
            torch.from_numpy(self.m_art[idx]),
            torch.from_numpy(self.pollutants_true[idx]),
            torch.from_numpy(self.eval_mask[idx])
        )

def train_imputation_model(
    model: nn.Module,
    train_dataset: PollutionImputationDataset,
    val_dataset: PollutionImputationDataset,
    epochs: int = 40,
    batch_size: int = 64,
    learning_rate: float = 0.001,
    weight_decay: float = 1e-4,
    patience: int = 8,
    checkpoint_dir: str = "checkpoints",
    device: str = "auto",
    loss_type: str = "smooth_l1"
) -> Tuple[nn.Module, Dict[str, list]]:
    """
    Trains the imputation neural network with early stopping, dynamic masking, and CosineAnnealingLR.
    """
    if device == "auto":
        dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        dev = torch.device(device)
        
    if dev.type == "cpu" and hasattr(torch, "set_num_threads"):
        torch.set_num_threads(min(12, os.cpu_count() or 8))
        
    model = model.to(dev)
    os.makedirs(checkpoint_dir, exist_ok=True)
    best_model_path = os.path.join(checkpoint_dir, "best_temporal_transformer.pt")
    tb_logdir = os.path.join("runs", os.path.basename(checkpoint_dir) or "default")
    tb_writer = SummaryWriter(log_dir=tb_logdir) if SummaryWriter is not None else None
    
    train_loader = DataLoader(
        train_dataset, 
        batch_size=batch_size, 
        shuffle=True, 
        drop_last=False,
        num_workers=0,
        pin_memory=(dev.type == "cuda")
    )
    val_loader = DataLoader(
        val_dataset, 
        batch_size=batch_size, 
        shuffle=False,
        num_workers=0,
        pin_memory=(dev.type == "cuda")
    )
    
    criterion = MaskedImputationLoss(loss_type=loss_type)
    eval_criterion = MaskedImputationLoss(loss_type="l1")  # Pure MAE for validation metric
    
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=weight_decay)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-5)
    
    history = {"train_loss": [], "val_loss": [], "epoch_times": []}
    best_val_loss = float("inf")
    patience_counter = 0
    
    print(f"[Training] Beginning model training on device: {dev} for {epochs} epochs...")
    print(f"[Training] Optimizer: AdamW (lr={learning_rate}, weight_decay={weight_decay}) | Loss: {loss_type}")
    
    for epoch in range(1, epochs + 1):
        t0 = time.time()
        if hasattr(train_dataset, "dynamic_masking") and train_dataset.dynamic_masking:
            train_dataset.regenerate_epoch_masks()
            
        model.train()
        train_losses = []
        
        for x_obs, m_art, x_true, eval_m in train_loader:
            x_obs = x_obs.to(dev)
            m_art = m_art.to(dev)
            x_true = x_true.to(dev)
            eval_m = eval_m.to(dev)
            
            optimizer.zero_grad()
            _, x_pred_raw = model(x_obs, m_art)
            loss = criterion(x_pred_raw, x_true, eval_m)
            
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            
            train_losses.append(loss.item())
            
        scheduler.step()
        avg_train_loss = float(np.mean(train_losses))
        
        # Validation (computed in pure L1 / MAE)
        model.eval()
        val_losses = []
        with torch.no_grad():
            for x_obs, m_art, x_true, eval_m in val_loader:
                x_obs = x_obs.to(dev)
                m_art = m_art.to(dev)
                x_true = x_true.to(dev)
                eval_m = eval_m.to(dev)
                
                _, x_pred_raw = model(x_obs, m_art)
                v_loss = eval_criterion(x_pred_raw, x_true, eval_m)
                val_losses.append(v_loss.item())
                
        avg_val_loss = float(np.mean(val_losses))
        current_lr = scheduler.get_last_lr()[0]
        
        duration = time.time() - t0
        history["train_loss"].append(avg_train_loss)
        history["val_loss"].append(avg_val_loss)
        history["epoch_times"].append(duration)
        
        is_best = avg_val_loss < best_val_loss
        if is_best:
            best_val_loss = avg_val_loss
            patience_counter = 0
            torch.save(model.state_dict(), best_model_path)
            mark = "★ BEST"
        else:
            patience_counter += 1
            mark = f"(patience {patience_counter}/{patience})"
            
        if tb_writer is not None:
            tb_writer.add_scalar("Loss/train", avg_train_loss, epoch)
            tb_writer.add_scalar("Loss/val_mae", avg_val_loss, epoch)
            tb_writer.add_scalar("Learning_Rate", current_lr, epoch)
            tb_writer.add_scalar("Time/epoch_seconds", duration, epoch)
            
        print(f"Epoch {epoch:02d}/{epochs:02d} | Train Loss: {avg_train_loss:.4f} | Val MAE: {avg_val_loss:.4f} | LR: {current_lr:.1e} | Time: {duration:.2f}s {mark}")
        
        if patience_counter >= patience:
            print(f"[Training] Early stopping triggered at epoch {epoch}. Best Val MAE: {best_val_loss:.4f}")
            break
            
    if tb_writer is not None:
        tb_writer.close()
            
    if os.path.exists(best_model_path):
        model.load_state_dict(torch.load(best_model_path, map_location=dev))
        print(f"[Training] Restored best checkpoint from {best_model_path} (Val MAE: {best_val_loss:.4f})")
        
    return model, history
