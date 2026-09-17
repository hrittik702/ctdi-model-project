import pandas as pd
import numpy as np

total = 55876
h_counts = [8956, 1998, 2962, 5728, 1399, 1088, 1105, 1042, 1139, 1690, 3750, 4189, 3736, 3210, 2964, 2526, 1878, 1301, 979, 786, 688, 707, 757, 1298]
props = [c / total * 100 for c in h_counts]

print("1 decimal place:")
print([f"{p:.1f}%" for p in props[:5]])

print("Integer:")
print([f"{round(p)}%" for p in props[:5]])

p_counts = [10657, 11395, 11651, 11056, 11117]
p_props = [c / total * 100 for c in p_counts]
print("\nPollutants 1 dec:")
print([f"{p:.1f}%" for p in p_props])
print("Pollutants int:")
print([f"{round(p)}%" for p in p_props])
