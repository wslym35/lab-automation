#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 15 11:21:09 2026

@author: wkmills
"""

import numpy as np
import pandas as pd
from scipy.signal import find_peaks
import matplotlib.pyplot as plt

# ── 1.  Load the CSV ──────────────────────────────────────────────────────────
# Assumption: CSV is a 2-D array of count values, rows = output k, cols = input k
# Adjust sep/header/index_col to match your actual file format.

csv_file = "case5-QW540nm-thinDSP_pp_SHG_counts.csv"
data = pd.read_csv(csv_file, header=0, index_col=0)   # shape: (N_kout, N_kin)

counts = data.values.astype(float)          # 2-D numpy array
k_in_axis  = np.linspace(-1.3, +1.3, np.shape(counts)[1])    # 1-D array of input  k‖/k₀ values
k_out_axis = np.linspace(-1.3, +1.3, np.shape(counts)[0])    # 1-D array of output k‖/k₀ values

# ── 2.  Grating parameters ────────────────────────────────────────────────────
# Read the grating momentum off the plot: the m=+1 diagonal is offset from the
# main diagonal by delta_k.  Adjust this value to match your grating.
def estimate_delta_k(counts, k_in_axis, k_out_axis):
    """
    Project the 2D heatmap onto the offset axis (k_out - k_in) and find
    the spacing between diffraction order peaks.
    """
    # ── 1. Build a 1-D projection onto (k_out - k_in) ────────────────────────
    # For every pixel, compute its offset and accumulate counts into a 1-D histogram.
    
    K_in, K_out = np.meshgrid(k_in_axis, k_out_axis)   # both shape (N_kout, N_kin)
    offsets = (K_out - K_in).ravel()
    weights = counts.ravel()

    offset_min = offsets.min()
    offset_max = offsets.max()
    n_bins = 2 * len(k_in_axis)   # resolution ~ half the k_in pixel size

    projection, bin_edges = np.histogram(offsets, bins=n_bins,
                                         range=(offset_min, offset_max),
                                         weights=weights)
    bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])

    # ── 2. Find peaks in the projection ──────────────────────────────────────
    # Peaks correspond to diffraction orders; their spacing is delta_k.
    peaks, props = find_peaks(projection,
                              height=projection.max() * 0.2,  # ignore noise floor
                              distance=n_bins // 20)           # min separation

    peak_offsets = bin_centers[peaks]

    # ── 3. Estimate delta_k from the median inter-peak spacing ───────────────
    if len(peak_offsets) < 2:
        raise ValueError("Fewer than 2 peaks found — try lowering the height threshold.")

    spacings = np.diff(np.sort(peak_offsets))
    delta_k  = np.median(spacings)

    return delta_k, bin_centers, projection, peak_offsets

delta_k = estimate_delta_k(counts, k_in_axis, k_out_axis)[0]          # grating momentum in units of k₀  (looks ~0.5 from image)

orders  = [-2, -1, 0, 1, 2]

# ── 3.  k_in range for each order ─────────────────────────────────────────────
# Only keep k_in values where k_out = k_in + m*delta_k is within the measured
# output axis range.
k_in_min = k_in_axis.min()
k_in_max = k_in_axis.max()
k_out_min = k_out_axis.min()
k_out_max = k_out_axis.max()

def k_in_range_for_order(m):
    """Return the k_in values for which k_out stays inside the measured window."""
    # k_out = k_in + m*delta_k  =>  k_in = k_out - m*delta_k
    lo = max(k_in_min, k_out_min - m * delta_k)
    hi = min(k_in_max, k_out_max - m * delta_k)
    mask = (k_in_axis >= lo) & (k_in_axis <= hi)
    return k_in_axis[mask]

# ── 4.  Interpolate counts along each diagonal ───────────────────────────────
from scipy.interpolate import RegularGridInterpolator

interp = RegularGridInterpolator(
    (k_out_axis, k_in_axis),   # note: (row-axis, col-axis)
    counts,
    method="linear",
    bounds_error=False,
    fill_value=0.0,
)

# =============================================================================
# def extract_order(m):
#     k_in  = k_in_range_for_order(m)
#     k_out = k_in + m * delta_k          # the diagonal condition
#     pts   = np.column_stack([k_out, k_in])
#     vals  = interp(pts)
#     return k_in, vals
# =============================================================================

def extract_order_integrated(m, half_width=.15):
    k_in = k_in_range_for_order(m)
    vals = []
    for ki in k_in:
        k_out_center = ki + m * delta_k
        mask = np.abs(k_out_axis - k_out_center) < half_width
        vals.append(counts[mask, :][: , np.argmin(np.abs(k_in_axis - ki))].sum())
    return k_in, np.array(vals)

# ── 5.  Plot ──────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(6, 6))

colors = plt.cm.coolwarm(np.linspace(0, 1, len(orders)))
colors[len(colors)//2] = [0,0,0,1] # Make m=0 black 

for m, color in zip(orders[::-1], colors[::-1]):
    k_in, vals = extract_order_integrated(m)
    ax.plot(k_in, vals, label=f"m = {m:+d}", color=color, linewidth=3, alpha=0.8)

ax.set_xlabel(r"Input $k_\parallel / k_0$")
ax.set_ylabel("Counts")
ax.set_title("Diffraction order intensities vs input momentum\n" + csv_file[:-4])
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.gca().set_box_aspect(1)
plt.savefig(csv_file[:-4] + '_diffraction-orders.png', dpi=150)
plt.show()


# ── Quick sanity-check plot ───────────────────────────────────────────────────
delta_k, bin_centers, projection, peak_offsets = estimate_delta_k(
    counts, k_in_axis, k_out_axis
)
print(f"Estimated delta_k = {delta_k:.4f} k₀")

import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(8, 3))
ax.plot(bin_centers, projection)
ax.vlines(peak_offsets, 0, projection.max(), color="r",
          linestyle="--", label="detected orders")
ax.set_xlabel(r"$k_{\rm out} - k_{\rm in}$  ($k_0$)")
ax.set_ylabel("Projected counts")
ax.set_title("Projection onto offset axis — peaks = diffraction orders")
ax.legend()
plt.tight_layout()
plt.show()
