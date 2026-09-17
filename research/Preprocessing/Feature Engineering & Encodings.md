# Feature Engineering & Temporal Encodings

---

## 1. Cyclical Sine/Cosine Temporal Embeddings

To encode periodic atmospheric rhythms without introducing artificial mathematical discontinuities at midnight (23:00 to 00:00) or year-end (December 31 to January 1), we project timestamps onto continuous unit circles:

### 1.1 Diurnal Cycle (Hour of Day: $h \in [0, 23]$)
$$\sin_{\text{hour}} = \sin\left(\frac{2\pi \cdot h}{24}\right), \quad \cos_{\text{hour}} = \cos\left(\frac{2\pi \cdot h}{24}\right)$$

### 1.2 Weekly Cycle (Day of Week: $d \in [0, 6]$)
$$\sin_{\text{dow}} = \sin\left(\frac{2\pi \cdot d}{7}\right), \quad \cos_{\text{dow}} = \cos\left(\frac{2\pi \cdot d}{7}\right)$$

### 1.3 Annual Seasonal Cycle (Month of Year: $m \in [1, 12]$)
$$\sin_{\text{month}} = \sin\left(\frac{2\pi \cdot (m - 1)}{12}\right), \quad \cos_{\text{month}} = \cos\left(\frac{2\pi \cdot (m - 1)}{12}\right)$$

---

## 2. Spatial Coordinate Embeddings

For model layers incorporating spatial attention, monitoring station metadata (latitude, longitude, sampling height, and station type) are normalized and embedded:
$$\mathbf{e}_{\text{spatial}}(s) = \text{MLP}\left( [\text{norm}(\text{lat}_s), \text{norm}(\text{lon}_s), \text{norm}(\text{height}_s), \text{one\_hot}(\text{type}_s)] \right)$$
