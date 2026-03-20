import os
import re
import glob
import numpy as np
import matplotlib.pyplot as plt

# --- ky -> y-center mapping
while True:
    try:
        y_pos1 = float(input("Enter the y-pixel that corresponds to ky=+1 (e.g. 200): ").strip())
        y_neg1 = float(input("Enter the y-pixel that corresponds to ky=-1 (e.g. 800): ").strip())
        break
    except ValueError:
        print("Invalid input — please enter numeric pixel values (integers or floats). Try again.\n")

# Linear mapping parameters: y = m*ky + c
m_ky_to_y = (y_pos1 - y_neg1) / 2.0
c_ky_to_y = (y_pos1 + y_neg1) / 2.0

def ky_to_y(ky_value):
    """Return the (float) y pixel corresponding to ky_value using linear mapping."""
    return m_ky_to_y * ky_value + c_ky_to_y

# --- parameters for ROI and folder ---
DATA_FOLDER = "03-06 glass reflection"   # relative path
FILE_GLOB = os.path.join(DATA_FOLDER, "*ky=*_*ms.csv")  # matches e.g. ...ky=+0.10_...csv
CENTER_X = 512

# Ask ROI size once for the whole run
while True:
    try:
        ROI_w = int(input("Enter ROI width in pixels (e.g. 11): ").strip())
        ROI_h = int(input("Enter ROI height in pixels (e.g. 11): ").strip())
        if ROI_w <= 0 or ROI_h <= 0:
            print("Width and height must be positive integers.")
            continue
        break
    except ValueError:
        print("Invalid input. Please enter integer values.")

# --- helper: compute avg using same idea as your get_avg function (simplified) ---
def get_avg_from_file(data_file, dimensions, bkgrnd_choice='None', background_file=None):
    """
    dimensions: ((x0,y0),(x1,y1)) inclusive pixel coords
    bkgrnd_choice: implemented only for 'None' here. If you need others, expand similarly.
    """
    (x0, y0), (x1, y1) = dimensions
    # safety: ensure non-negative and x1/x0 integer
    x0 = int(max(0, x0))
    x1 = int(max(0, x1))
    y0 = int(max(0, y0))
    y1 = int(max(0, y1))

    # load the ROI: CSV assumed rows ~ y (vertical) and columns ~ x (horizontal)
    # skiprows=2 + y0 to start reading at the correct CSV row (matches your function)
    ncols = x1 - x0 + 1
    nrows = y1 - y0 + 1
    # usecols expects indices of columns to load
    usecols = tuple(range(x0, x1 + 1))

    try:
        data = np.loadtxt(data_file, delimiter=',', skiprows=2 + y0, max_rows=nrows, usecols=usecols)
    except Exception as e:
        raise RuntimeError(f"Error loading {data_file} ROI: {e}")

    if data.size == 0:
        raise RuntimeError(f"No data read from {data_file} for ROI {((x0,y0),(x1,y1))}")

    # flatten and compute average
    avg = np.sum(data) / (ncols * nrows)

    # for simplicity, only 'None' background option implemented (as you asked).
    # If you want sapphire/k-mirror/full_kspace, we can add them back in with exact rules.
    return np.round(avg)

# --- find files and parse ky from filename ---
file_list = sorted(glob.glob(os.path.join(DATA_FOLDER, "*.csv")))

pattern = re.compile(r"ky=([+-]?\d+[.,]\d+|[+-]?\d+)")
#pattern = re.compile(r"ky=([+-]?\d+\.\d+|[+-]?\d+)")  # captures ky value like +0.10 or -1.3 etc.

ky_vals = []
avg_vals = []
bad_files = []

for f in file_list:
    m = pattern.search(os.path.basename(f))
    if not m:
        # skip files that don't match
        continue
    ky_str = m.group(1)
    ky = float(ky_str)
    # normalize ky to the format used in mapping: round to 1 decimal place (e.g. +0.10 -> 0.1)
    # this helps match keys like 0.1, -1.3 etc
    cy = ky_to_y(ky)
    cx = CENTER_X

    # compute ROI bounds from center and ROI_w/ROI_h (center included)
    # We'll create symmetric ROI: floor on left/top, ceil on right/bottom when even/odd differences
    half_w = ROI_w // 2
    half_h = ROI_h // 2
    x0 = cx - half_w
    x1 = x0 + ROI_w - 1
    y0 = cy - half_h
    y1 = y0 + ROI_h - 1

    try:
        avg = get_avg_from_file(f, ((x0, y0), (x1, y1)), bkgrnd_choice='None')
    except Exception as e:
        bad_files.append((f, str(e)))
        continue

    ky_vals.append(ky)
    avg_vals.append(float(avg))

# sort arrays by ky
sorted_pairs = sorted(zip(ky_vals, avg_vals), key=lambda p: p[0])
if not sorted_pairs:
    raise SystemExit("No matching CSV files found or no ky keys matched the mapping. Check folder and filenames.")

ky_sorted = np.array([p[0] for p in sorted_pairs])
avg_sorted = np.array([p[1] for p in sorted_pairs])

# normalize by maximum
max_val = np.max(avg_sorted)
if max_val == 0:
    norm = avg_sorted
else:
    norm = avg_sorted / max_val

# save a summary CSV with ky, avg, norm
summary_csv = os.path.join(DATA_FOLDER, "summary_normalized_avg_vs_ky.csv")
with open(summary_csv, 'w', newline='') as out:
    out.write("ky,avg,norm\n")
    for k, a, n in zip(ky_sorted, avg_sorted, norm):
        out.write(f"{k:+0.6f},{a:.6f},{n:.6f}\n")

# --- plot ---
plt.figure(figsize=(8,5))
plt.plot(ky_sorted, norm, marker='o', linestyle='-')
plt.xlabel('ky')
plt.ylabel('Normalized average counts (divided by max)')
plt.title('Normalized average photon counts vs ky')
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(DATA_FOLDER, "normalized_avg_vs_ky.png"), dpi=150)
plt.show()

# --- print summary ---
print("Processed files (ky -> normalized avg):")
for k, v in zip(ky_sorted, norm):
    print(f"{k:+0.1f} -> {v:.4f}")

if bad_files:
    print("\nSome files were skipped or had errors:")
    for item in bad_files:
        print(item)