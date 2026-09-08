"""Training and validation loop for neural imputation models."""

import os
import time
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from typing import Dict, Any, Optional, Tuple
from src.training.losses import MaskedImputationLoss

class PollutionImputationDataset(Dataset):
    """Dataset packaging observed data, visibility mask, ground truth, and evaluation mask."""
    def __init__(
        self,
        x_obs: np.ndarray,
        m_art: np.ndarray,
        x_true: np.ndarray,
        eval_mask: np.ndarray
    ):
        self.x_obs = torch.tensor(x_obs, dtype=torch.float32)
        self.m_art = torch.tensor(m_art, dtype=torch.float32)
        self.x_true = torch.tensor(np.nan_to_num(x_true, nan=0.0), dtype=torch.float32)
        self.eval_mask = torch.tensor(eval_mask, dtype=torch.float32)
        
    def __len__(self) -> int:
        return len(self.x_obs)
        
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        return (
            self.x_obs[idx],
            self.m_art[idx],
            self.x_true[idx],
            self.eval_mask[idx]
        )

def train_imputation_model(
    model: nn.Module,
    train_dataset: PollutionImputationDataset,
    val_dataset: PollutionImputationDataset,
    epochs: int = 20,
    batch_size: int = 64,
    learning_rate: float = 0.001,
    weight_decay: float = 1e-4,
    patience: int = 5,
    checkpoint_dir: str = "checkpoints",
    device: str = "auto"
) -> Tuple[nn.Module, Dict[str, list]]:
    """
    Trains the imputation neural network with early stopping and masked loss.
    """
    if device == "auto":
        dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        dev = torch.device(device)
        
    model = model.to(dev)
    os.makedirs(checkpoint_dir, exist_ok=True)
    best_model_path = os.path.join(checkpoint_dir, "best_temporal_transformer.pt")
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, drop_last=False)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    
    criterion = MaskedImputationLoss(loss_type="l1")
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=weight_decay)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="min", factor=0.5, patience=2)
    
    history = {"train_loss": [], "val_loss": [], "epoch_times": []}
    best_val_loss = float("inf")
    patience_counter = 0
    
    print(f"[Training] Beginning model training on device: {dev} for {epochs} epochs...")
    
    for epoch in range(1, epochs + 1):
        t0 = time.time()
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
            
        avg_train_loss = float(np.mean(train_losses))
        
        # Validation
        model.eval()
        val_losses = []
        with torch.no_grad():
            for x_obs, m_art, x_true, eval_m in val_loader:
                x_obs = x_obs.to(dev)
                m_art = m_art.to(dev)
                x_true = x_true.to(dev)
                eval_m = eval_m.to(dev)
                
                _, x_pred_raw = model(x_obs, m_art)
                v_loss = criterion(x_pred_raw, x_true, eval_m)
                val_losses.append(v_loss.item())
                
        avg_val_loss = float(np.mean(val_losses))
        scheduler.step(avg_val_loss)
        
        duration = time.time() - t0
        history["train_loss"].append(avg_train_loss)
        history["val_loss"].append(avg_val_loss)
        history["epoch_times"].append(duration)
        
        print(f"Epoch {epoch:02d}/{epochs:02d} | Train Loss (MAE): {avg_train_loss:.4f} | Val Loss: {avg_val_loss:.4f} | Time: {duration:.2f}s")
        
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            patience_counter = 0
            torch.save(model.state_dict(), best_model_path)
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"[Training] Early stopping triggered at epoch {epoch}. Best Val Loss: {best_val_loss:.4f}")
                break
                
    if os.path.exists(best_model_path):
        model.load_state_dict(torch.load(best_model_path, map_location=dev))
        print(f"[Training] Loaded best model checkpoint from {best_model_path}")
        
    return model, history
