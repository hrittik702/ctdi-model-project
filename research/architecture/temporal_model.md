# Temporal Model: Transformer Denoising Blocks

---

## 1. 24-Hour Temporal Self-Attention

To capture diurnal air pollution dynamics across the 24-hour sequence ($K = 24$), each residual block incorporates multi-head temporal self-attention:

$$\mathbf{Q} = \mathbf{H} \mathbf{W}_Q, \quad \mathbf{K} = \mathbf{H} \mathbf{W}_K, \quad \mathbf{V} = \mathbf{H} \mathbf{W}_V$$
$$\text{Attention}(\mathbf{Q}, \mathbf{K}, \mathbf{V}) = \text{softmax}\left(\frac{\mathbf{Q}\mathbf{K}^T}{\sqrt{d_k}} + \mathbf{B}_{\text{rel}}\right) \mathbf{V}$$

where:
- $\mathbf{B}_{\text{rel}}$ is a learnable relative positional bias encoding hour-to-hour intervals $\Delta t = |t_1 - t_2|$.
- Dimension: Computed across $K = 24$ tokens independently for each of the $S = 16$ stations, avoiding quadratic scaling over the joint $S \times K$ space.

---

## 2. Feed-Forward Gated Network
Following self-attention, features pass through a gated activation unit:
$$\text{FFN}(\mathbf{u}) = (\mathbf{u} \mathbf{W}_1 + \mathbf{b}_1) \odot \text{sigmoid}(\mathbf{u} \mathbf{W}_2 + \mathbf{b}_2)$$
with residual connections: $\mathbf{H}_{\text{out}} = \text{LayerNorm}(\mathbf{H}_{\text{in}} + \text{FFN}(\mathbf{u}))$.
