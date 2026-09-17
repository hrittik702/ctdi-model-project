# Conditioning Mechanism: AdaLN & Cross-Attention

---

## 1. Dual Conditioning Architecture

The conditional denoising network incorporates two complementary conditioning streams:
1. **Low-Level Numerical Conditioning**: The masked observation tensor $\mathbf{x}_0 \odot \mathbf{M}$ and diffusion step embedding $\mathbf{e}_k$.
2. **High-Level Semantic Conditioning**: The SLM context vector $\mathbf{z}_C \in \mathbb{R}^{d_{\text{diff}}}$.

---

## 2. Adaptive Layer Normalization (AdaLN)

For intermediate residual feature maps $\mathbf{h} \in \mathbb{R}^{B \times S \times K \times d}$, AdaLN dynamically modulates scale and shift:

$$\text{AdaLN}(\mathbf{h}, \mathbf{z}_C, \mathbf{e}_k) = \boldsymbol{\gamma}(\mathbf{z}_C + \mathbf{e}_k) \odot \left( \frac{\mathbf{h} - \mu(\mathbf{h})}{\sigma(\mathbf{h})} \right) + \boldsymbol{\beta}(\mathbf{z}_C + \mathbf{e}_k)$$

where:
- $\boldsymbol{\gamma}(\cdot)$ and $\boldsymbol{\beta}(\cdot)$ are linear projection heads initialized near zero (so initial training matches unconditioned dynamics).
- $\mu(\mathbf{h})$ and $\sigma(\mathbf{h})$ are channel-wise mean and standard deviation.

---

## 3. Cross-Attention Option

For fine-grained multi-token token prompt conditioning:
$$\mathbf{H}_{\text{cross}} = \text{softmax}\left(\frac{\mathbf{H} \mathbf{W}_Q (\mathbf{H}_{\text{slm}} \mathbf{W}_K)^T}{\sqrt{d_k}}\right) \mathbf{H}_{\text{slm}} \mathbf{W}_V$$
where queries come from intermediate spatio-temporal features, and keys/values come from the tokenized SLM sequence.
