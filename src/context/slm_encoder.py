"""SLM Context Encoder interface and architecture specification.

Defines the neural interface mapping structured text prompt sequences C into
dense semantic conditioning vectors z_C for the conditional diffusion backbone:

    C -> [Tokenizer] -> [Frozen SLM Backbone] -> H in R^(L x d_slm)
      -> [Pooling (mean/last/attn)] -> z_raw in R^(d_slm)
      -> [Trainable Projection Head W_p] -> z_C in R^(d_diff)

The SLM functions strictly as a semantic context encoder. It never outputs raw
pollution concentrations directly.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Union
import hashlib
import torch
import torch.nn as nn
import torch.nn.functional as F


class BaseSLMContextEncoder(nn.Module, ABC):
    """Abstract base class for SLM context encoders."""

    def __init__(
        self,
        d_slm: int = 896,
        d_diff: int = 128,
        pooling_strategy: str = "mean",
        freeze_backbone: bool = True,
        use_layer_norm: bool = True,
    ):
        """Initialize base encoder.
        
        Args:
            d_slm: Hidden embedding dimension of the SLM backbone (e.g. 896 for Qwen-2.5-0.5B).
            d_diff: Conditioning dimension of the diffusion model (e.g. 128).
            pooling_strategy: 'mean', 'last_token', or 'attention_pool'.
            freeze_backbone: If True, backbone parameters have requires_grad=False.
            use_layer_norm: Whether to apply LayerNorm to projected context vector z_C.
        """
        super().__init__()
        self.d_slm = d_slm
        self.d_diff = d_diff
        self.pooling_strategy = pooling_strategy.lower().strip()
        self.freeze_backbone = freeze_backbone
        self.use_layer_norm = use_layer_norm

        if self.pooling_strategy not in ["mean", "last_token", "attention_pool"]:
            raise ValueError(f"Unsupported pooling strategy: {self.pooling_strategy}")

        # Trainable projection head mapping SLM hidden state to diffusion conditioning dimension
        self.projection = nn.Linear(self.d_slm, self.d_diff, bias=True)
        self.layer_norm = nn.LayerNorm(self.d_diff) if use_layer_norm else nn.Identity()

        # Attention pooling query if attention_pool strategy selected
        if self.pooling_strategy == "attention_pool":
            self.pool_query = nn.Parameter(torch.randn(1, 1, self.d_slm) * 0.02)

    def pool_tokens(
        self,
        token_embeddings: torch.Tensor,
        attention_mask: torch.Tensor,
    ) -> torch.Tensor:
        """Pool token representations H in R^(B x L x d_slm) to z_raw in R^(B x d_slm).
        
        Args:
            token_embeddings: Tensor of shape (B, L, d_slm).
            attention_mask: Binary tensor of shape (B, L) where 1=valid, 0=padding.
            
        Returns:
            Pooled representation z_raw of shape (B, d_slm).
        """
        b, l, d = token_embeddings.shape

        if self.pooling_strategy == "mean":
            # Masked average across non-padding tokens
            mask_expanded = attention_mask.unsqueeze(-1).expand_as(token_embeddings).float()
            sum_embeddings = torch.sum(token_embeddings * mask_expanded, dim=1)
            sum_mask = torch.clamp(mask_expanded.sum(dim=1), min=1e-9)
            return sum_embeddings / sum_mask

        elif self.pooling_strategy == "last_token":
            # Extract last non-padding token representation
            lengths = attention_mask.sum(dim=1).long() - 1  # 0-indexed last token
            lengths = torch.clamp(lengths, min=0)
            batch_indices = torch.arange(b, device=token_embeddings.device)
            return token_embeddings[batch_indices, lengths]

        elif self.pooling_strategy == "attention_pool":
            # Multi-head / query attention pooling
            # score = softmax(Query @ H^T / sqrt(d)) @ H
            q = self.pool_query.expand(b, -1, -1)  # (B, 1, d_slm)
            scores = torch.bmm(q, token_embeddings.transpose(1, 2)) / (d ** 0.5)  # (B, 1, L)
            # Mask out padding tokens with large negative value
            scores = scores.masked_fill(attention_mask.unsqueeze(1) == 0, -1e9)
            attn_weights = F.softmax(scores, dim=-1)  # (B, 1, L)
            pooled = torch.bmm(attn_weights, token_embeddings)  # (B, 1, d_slm)
            return pooled.squeeze(1)

        raise ValueError(f"Unknown pooling strategy: {self.pooling_strategy}")

    def project_context(self, z_raw: torch.Tensor) -> torch.Tensor:
        """Project pooled SLM representation to diffusion conditioning vector z_C.
        
        Formula:
            z_C = LayerNorm(W_p * z_raw + b_p)
            
        Args:
            z_raw: Tensor of shape (B, d_slm).
            
        Returns:
            z_C: Conditioning vector of shape (B, d_diff).
        """
        z_proj = self.projection(z_raw)
        return self.layer_norm(z_proj)

    @abstractmethod
    def encode_tokens(self, prompts: List[str]) -> Tuple[torch.Tensor, torch.Tensor]:
        """Tokenize prompts and run backbone forward pass.
        
        Args:
            prompts: List of B serialized prompt strings.
            
        Returns:
            Tuple of (token_embeddings, attention_mask):
                token_embeddings: (B, L, d_slm)
                attention_mask: (B, L)
        """
        pass

    def forward(self, prompts: List[str]) -> torch.Tensor:
        """End-to-end forward mapping: Prompts -> z_C.
        
        Args:
            prompts: List of B prompt strings.
            
        Returns:
            z_C: Conditioning tensor of shape (B, d_diff).
        """
        token_embeddings, attention_mask = self.encode_tokens(prompts)
        z_raw = self.pool_tokens(token_embeddings, attention_mask)
        z_C = self.project_context(z_raw)
        return z_C


class MockSLMContextEncoder(BaseSLMContextEncoder):
    """Deterministic Mock SLM Context Encoder for scaffolding, testing, and validation.
    
    Generates reproducible continuous embeddings from prompt strings without requiring
    external Hugging Face downloads or GPU memory. Perfect for pipeline verification.
    """

    def __init__(
        self,
        d_slm: int = 896,
        d_diff: int = 128,
        pooling_strategy: str = "mean",
        freeze_backbone: bool = True,
        use_layer_norm: bool = True,
    ):
        super().__init__(
            d_slm=d_slm,
            d_diff=d_diff,
            pooling_strategy=pooling_strategy,
            freeze_backbone=freeze_backbone,
            use_layer_norm=use_layer_norm,
        )

    def encode_tokens(self, prompts: List[str]) -> Tuple[torch.Tensor, torch.Tensor]:
        """Synthesize deterministic token representations using sha256 hashing."""
        b = len(prompts)
        max_len = 32  # simulated fixed token sequence length
        
        tokens_list = []
        masks_list = []

        for p in prompts:
            # Deterministic pseudo-embedding based on hash digest
            h = hashlib.sha256(p.encode("utf-8")).digest()
            # Seed a generator with first 4 bytes
            seed = int.from_bytes(h[:4], "big")
            g = torch.Generator().manual_seed(seed)
            # Simulated token sequence (max_len, d_slm)
            seq = torch.randn(max_len, self.d_slm, generator=g)
            
            # Simulated attention mask (variable active length based on string length)
            active_len = min(max_len, max(8, len(p) % max_len))
            mask = torch.zeros(max_len, dtype=torch.long)
            mask[:active_len] = 1

            tokens_list.append(seq)
            masks_list.append(mask)

        token_embeddings = torch.stack(tokens_list, dim=0)  # (B, max_len, d_slm)
        attention_mask = torch.stack(masks_list, dim=0)    # (B, max_len)

        # In a frozen backbone, detach token embeddings so no gradients flow to backbone
        if self.freeze_backbone:
            token_embeddings = token_embeddings.detach()

        return token_embeddings, attention_mask


class HuggingFaceSLMContextEncoder(BaseSLMContextEncoder):
    """Production architecture specification for HuggingFace pre-trained SLMs.
    
    Loads pre-trained causal or masked language model weights (e.g. Qwen2.5-0.5B,
    Llama-3.2-1B, Phi-3-Mini) and extracts contextual token hidden states.
    
    NOTE: In Phase 4A, this class serves as the formal architectural specification.
    Model weight downloading and execution will be activated in later training phases.
    """

    def __init__(
        self,
        model_name_or_path: str = "Qwen/Qwen2.5-0.5B",
        d_diff: int = 128,
        pooling_strategy: str = "mean",
        freeze_backbone: bool = True,
        use_layer_norm: bool = True,
        torch_dtype: Optional[torch.dtype] = None,
        device: Optional[Union[str, torch.device]] = None,
        max_length: int = 512,
    ):
        # We query the model dimension dynamically upon initialization or use defaults
        # Common SLM dimensions: Qwen2.5-0.5B=896, Llama-3.2-1B=2048, Phi-3-Mini=3072
        d_slm_map = {
            "Qwen/Qwen2.5-0.5B": 896,
            "Qwen/Qwen2.5-1.5B": 1536,
            "meta-llama/Llama-3.2-1B": 2048,
            "microsoft/Phi-3-mini-4k-instruct": 3072,
            "google/gemma-2-2b": 2304,
        }
        d_slm = d_slm_map.get(model_name_or_path, 896)

        super().__init__(
            d_slm=d_slm,
            d_diff=d_diff,
            pooling_strategy=pooling_strategy,
            freeze_backbone=freeze_backbone,
            use_layer_norm=use_layer_norm,
        )
        self.model_name = model_name_or_path
        self.max_length = max_length
        self.target_device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.torch_dtype = torch_dtype or torch.float32

        self.tokenizer = None
        self.backbone = None
        self._is_loaded = False

    def load_model(self):
        """Lazy load HuggingFace tokenizer and backbone weights."""
        if self._is_loaded:
            return

        try:
            from transformers import AutoTokenizer, AutoModel
        except ImportError as e:
            raise ImportError(
                "transformers package is required for HuggingFaceSLMContextEncoder. "
                "Install via: pip install transformers"
            ) from e

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        self.backbone = AutoModel.from_pretrained(
            self.model_name,
            torch_dtype=self.torch_dtype,
        ).to(self.target_device)

        if self.freeze_backbone:
            for param in self.backbone.parameters():
                param.requires_grad = False
            self.backbone.eval()

        self._is_loaded = True

    def encode_tokens(self, prompts: List[str]) -> Tuple[torch.Tensor, torch.Tensor]:
        """Tokenize prompts and run frozen backbone forward pass."""
        if not self._is_loaded:
            raise RuntimeError(
                "Model is not loaded. Call encoder.load_model() before inference, "
                "or use MockSLMContextEncoder for architectural validation."
            )

        inputs = self.tokenizer(
            prompts,
            padding=True,
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt",
        ).to(self.target_device)

        with torch.set_grad_enabled(not self.freeze_backbone):
            outputs = self.backbone(**inputs)
            # Hidden states: shape (B, L, d_slm)
            token_embeddings = outputs.last_hidden_state

        return token_embeddings, inputs["attention_mask"]
