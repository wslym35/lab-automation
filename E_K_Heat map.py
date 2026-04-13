import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------
# File path (relative to project)
# ---------------------------

csv_file = os.path.join("SanUID033126-900SP_ss_R", "1080nm-1,27mW-spol-ky=+0,00_SanUID033126-900SP_spol-10ms.csv")

if not os.path.isfile(csv_file):
    raise FileNotFoundError(f"File not found: {csv_file}")

# ---------------------------
# Load CSV
# ---------------------------

# Read full CSV
df = pd.read_csv(csv_file, header=None)

# First row → wavelength (skip first column)
wavelengths = pd.to_numeric(df.iloc[0, 1:], errors='coerce').to_numpy()

# Remaining rows → photon counts
counts = df.iloc[1:, 1:].apply(pd.to_numeric, errors='coerce').to_numpy(dtype=float)

# y axis (pixel index)
y = np.arange(counts.shape[0])

# Remove invalid wavelength columns
valid = ~np.isnan(wavelengths)
wavelengths = wavelengths[valid]
counts = counts[:, valid]

# ---------------------------
# Plot heatmap
# ---------------------------

plt.figure(figsize=(10, 6))

X, Y = np.meshgrid(wavelengths, y)

plt.pcolormesh(X, Y, counts, shading='auto')
plt.xlabel("Wavelength (nm)")
plt.ylabel("y pixel")
plt.title("Photon Counts Heatmap")

plt.colorbar(label="Photon Counts")

plt.tight_layout()

# Save image
out_path = os.path.splitext(csv_file)[0] + "_heatmap.png"
plt.savefig(out_path, dpi=150)

plt.show()

print(f"Saved heatmap to: {out_path}")