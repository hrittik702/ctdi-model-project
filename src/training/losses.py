"""Loss functions for masked imputation training."""

import torch
import torch.nn as nn
from typing import Optional


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
            diff = nn.functional.smooth_l1_loss(x_pred, x_true, beta=0.1, reduction="none")
        else:
            raise ValueError(f"Unsupported loss_type: {self.loss_type}")
            
        masked_diff = diff * eval_mask
        total_eval_points = torch.sum(eval_mask)
        
        return torch.sum(masked_diff) / (total_eval_points + self.eps)


class PeakAwareImputationLoss(nn.Module):
    """
    Peak-Aware and Gradient-Aware Composite Imputation Loss:
    L = L_base + lambda_peak * L_peak + lambda_grad * L_grad

    1. L_base: Huber / Smooth L1 loss across masked evaluation positions.
    2. L_peak: Upweights top pollution values using (1.0 + lambda_peak * ReLU(y_true)),
       preventing the Transformer from regressing to the conditional mean on spikes.
    3. L_grad: Penalizes temporal gradient discrepancy |Delta y_pred - Delta y_true|,
       enforcing realistic rapid rises and falls instead of over-smoothed lines.
    4. pollutant_weights: Balanced scaling across PM2.5, PM10, NO2, SO2, O3.
    """
    def __init__(
        self,
        loss_type: str = "smooth_l1",
        lambda_peak: float = 1.0,
        lambda_grad: float = 0.5,
        pollutant_weights: Optional[torch.Tensor] = None,
        eps: float = 1e-6
    ):
        super().__init__()
        self.loss_type = loss_type.lower()
        self.lambda_peak = lambda_peak
        self.lambda_grad = lambda_grad
        self.eps = eps
        
        if pollutant_weights is not None:
            self.register_buffer("pollutant_weights", pollutant_weights.view(1, 1, -1))
        else:
            self.pollutant_weights = None

    def forward(
        self,
        x_pred: torch.Tensor,
        x_true: torch.Tensor,
        eval_mask: torch.Tensor
    ) -> torch.Tensor:
        """
        Args:
            x_pred: Predicted pollutants (B, T, F)
            x_true: Ground truth targets (B, T, F)
            eval_mask: 1 where artificially masked and ground truth exists (B, T, F)
        """
        # 1. Base error
        if self.loss_type == "l1":
            diff = torch.abs(x_pred - x_true)
        elif self.loss_type == "mse":
            diff = torch.square(x_pred - x_true)
        else:
            diff = nn.functional.smooth_l1_loss(x_pred, x_true, beta=0.1, reduction="none")

        # 2. Peak-weighting: higher weight for values exceeding the mean in normalized space
        # ReLU(x_true) is positive for values above mean (z > 0), giving peak events higher gradient
        peak_weight = 1.0 + self.lambda_peak * torch.relu(x_true)
        weighted_diff = diff * peak_weight * eval_mask
        
        if self.pollutant_weights is not None:
            weighted_diff = weighted_diff * self.pollutant_weights

        total_pts = torch.sum(eval_mask)
        if total_pts == 0:
            return torch.tensor(0.0, device=x_pred.device, requires_grad=True)

        base_loss = torch.sum(weighted_diff) / (total_pts + self.eps)

        # 3. Temporal rate-of-change / gradient loss
        if self.lambda_grad > 0.0 and x_pred.shape[1] > 1:
            diff_pred = x_pred[:, 1:, :] - x_pred[:, :-1, :]
            diff_true = x_true[:, 1:, :] - x_true[:, :-1, :]
            # Gradient mask: active if either boundary position was hidden
            grad_mask = ((eval_mask[:, 1:, :] + eval_mask[:, :-1, :]) > 0.0).float()
            grad_loss_element = torch.abs(diff_pred - diff_true) * grad_mask
            if self.pollutant_weights is not None:
                grad_loss_element = grad_loss_element * self.pollutant_weights
            grad_pts = torch.sum(grad_mask)
            grad_loss = torch.sum(grad_loss_element) / (grad_pts + self.eps) if grad_pts > 0 else 0.0
            return base_loss + self.lambda_grad * grad_loss

        return base_loss

