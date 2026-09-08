"""Loss functions for masked imputation training."""

import torch
import torch.nn as nn

class MaskedImputationLoss(nn.Module):
    """
    Computes loss EXCLUSIVELY on artificially hidden positions where ground truth is known.
    
    L = sum(|x_pred - x_true| * eval_mask) / (sum(eval_mask) + eps)
    """
    def __init__(self, loss_type: str = "l1", eps: float = 1e-6):
        super().__init__()
        self.loss_type = loss_type.lower()
        self.eps = eps
        
    def forward(
        self,
        x_pred: torch.Tensor,
        x_true: torch.Tensor,
        eval_mask: torch.Tensor
    ) -> torch.Tensor:
        """
        Args:
            x_pred: Model prediction (B, T, F)
            x_true: Ground truth target (B, T, F)
            eval_mask: 1 where artificially masked AND ground truth exists; 0 otherwise (B, T, F)
        """
        if self.loss_type == "l1":
            diff = torch.abs(x_pred - x_true)
        elif self.loss_type == "mse":
            diff = torch.square(x_pred - x_true)
        elif self.loss_type == "smooth_l1":
            diff = nn.functional.smooth_l1_loss(x_pred, x_true, reduction="none")
        else:
            raise ValueError(f"Unsupported loss_type: {self.loss_type}")
            
        masked_diff = diff * eval_mask
        total_eval_points = torch.sum(eval_mask)
        
        if total_eval_points == 0:
            return torch.tensor(0.0, device=x_pred.device, requires_grad=True)
            
        return torch.sum(masked_diff) / (total_eval_points + self.eps)
