import os
import re
import glob
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# -----------------------------
# Configuration
# -----------------------------
DATA_FOLDERS = [
    os.path.join(os.getcwd(), "SanUID033126-900SP_pp_R"),
    os.path.join(os.getcwd(), "SanUID033126-900SP_ss_R"),
]

FILE_GLOB = "*ky=*.csv"
KY_PATTERN = re.compile(r"(?:ky|k)=([+-]?\d+(?:[.,]\d+)?|[+-]?\.\d+)")
PLOT_ONLY_POSITIVE_KY = True


# -----------------------------
# Calibration: ky <-> y pixel
# -----------------------------
def load_calibration(data_folder):
    ky_cal_path = os.path.join(data_folder, "k_values.npy")
    pixel_cal_path = os.path.join(data_folder, "pixels.npy")

    if not os.path.exists(ky_cal_path):
        raise FileNotFoundError(f"Missing calibration file: {ky_cal_path}")
    if not os.path.exists(pixel_cal_path):
        raise FileNotFoundError(f"Missing calibration file: {pixel_cal_path}")

    ky_cal_data = np.load(ky_cal_path)
    pixel_cal_data = np.load(pixel_cal_path)

    y_pos1 = pixel_cal_data[np.argmin(np.abs(ky_cal_data - 1))]
    y_neg1 = pixel_cal_data[np.argmin(np.abs(ky_cal_data + 1))]

    m_ky_to_y = (y_pos1 - y_neg1) / 2.0
    c_ky_to_y = (y_pos1 + y_neg1) / 2.0

    if m_ky_to_y == 0:
        raise RuntimeError(f"Invalid calibration in {data_folder}: ky-to-y slope is zero.")

    return float(m_ky_to_y), float(c_ky_to_y)


def ky_to_y(ky_value, slope, intercept):
    return slope * ky_value + intercept


# -----------------------------
# Input helpers
# -----------------------------
def ask_positive_int(prompt):
    while True:
        try:
            value = int(input(prompt).strip())
            if value <= 0:
                print("Please enter a positive integer.")
                continue
            return value
        except ValueError:
            print("Invalid input. Please enter an integer.")


# -----------------------------
# Data loading
# -----------------------------
def load_counts_matrix(csv_file):
    try:
        df = pd.read_csv(csv_file, header=None, skiprows=1)
        df = df.apply(pd.to_numeric, errors="coerce")
    except Exception as exc:
        raise RuntimeError(f"Error reading {csv_file}: {exc}") from exc

    if df.empty or df.shape[1] < 2:
        raise RuntimeError(f"Unexpected or empty CSV format in {csv_file}")

    counts = df.iloc[:, 1:].to_numpy(dtype=float)

    if counts.size == 0:
        raise RuntimeError(f"No photon-count data found in {csv_file}")

    return counts


# -----------------------------
# ROI helpers
# -----------------------------
def find_x_center_from_counts(counts):
    if counts.ndim != 2 or counts.shape[1] == 0:
        raise RuntimeError("Counts array is empty or not 2D.")

    column_sums = np.nansum(counts, axis=0)
    return int(np.nanargmax(column_sums))


def get_roi_bounds(cx, cy, roi_w, roi_h, image_shape):
    nrows, ncols = image_shape

    if roi_w > ncols or roi_h > nrows:
        raise RuntimeError(
            f"ROI ({roi_w} x {roi_h}) is larger than image size ({ncols} x {nrows})."
        )

    cx = int(round(cx))
    cy = int(round(cy))

    half_w = roi_w // 2
    half_h = roi_h // 2

    x0 = cx - half_w
    y0 = cy - half_h
    x1 = x0 + roi_w
    y1 = y0 + roi_h

    x0 = max(0, min(x0, ncols - roi_w))
    y0 = max(0, min(y0, nrows - roi_h))
    x1 = x0 + roi_w
    y1 = y0 + roi_h

    return x0, x1, y0, y1


def get_avg_from_counts(counts, x0, x1, y0, y1):
    roi = counts[y0:y1, x0:x1]

    if roi.size == 0:
        raise RuntimeError(
            f"Empty ROI extracted: x=({x0}, {x1}), y=({y0}, {y1})"
        )

    return float(np.nanmean(roi))


# -----------------------------
# Filename parsing
# -----------------------------
def extract_ky_from_filename(file_path):
    file_name = os.path.basename(file_path)
    match = KY_PATTERN.search(file_name)
    if not match:
        raise ValueError(f"Could not extract ky from filename: {file_name}")
    return float(match.group(1).replace(",", "."))


# -----------------------------
# Folder processing
# -----------------------------
def process_folder(data_folder, roi_w, roi_h, positive_only=True):
    if not os.path.isdir(data_folder):
        raise FileNotFoundError(f"Data folder not found: {data_folder}")

    file_list = sorted(glob.glob(os.path.join(data_folder, FILE_GLOB)))
    if not file_list:
        raise FileNotFoundError(f"No CSV files matched in folder: {data_folder}")

    slope, intercept = load_calibration(data_folder)

    ky_vals = []
    avg_vals = []
    bad_files = []

    for csv_file in file_list:
        try:
            ky = extract_ky_from_filename(csv_file)

            if positive_only and ky <= 0:
                continue

            counts = load_counts_matrix(csv_file)
            cx = find_x_center_from_counts(counts)
            cy = ky_to_y(ky, slope, intercept)

            x0, x1, y0, y1 = get_roi_bounds(cx, cy, roi_w, roi_h, counts.shape)
            avg = get_avg_from_counts(counts, x0, x1, y0, y1)

            ky_vals.append(ky)
            avg_vals.append(avg)

        except Exception as exc:
            bad_files.append((os.path.basename(csv_file), str(exc)))

    if not ky_vals:
        raise RuntimeError(f"No files were successfully processed in {data_folder}")

    sorted_pairs = sorted(zip(ky_vals, avg_vals), key=lambda pair: pair[0])
    ky_sorted = np.array([pair[0] for pair in sorted_pairs], dtype=float)
    avg_sorted = np.array([pair[1] for pair in sorted_pairs], dtype=float)

    folder_name = os.path.basename(os.path.normpath(data_folder))
    summary_df = pd.DataFrame(
        {
            "ky": ky_sorted,
            "average_counts": avg_sorted,
        }
    )

    summary_csv = os.path.join(data_folder, f"summary_avg_counts_vs_ky_{folder_name}.csv")
    summary_df.to_csv(summary_csv, index=False)

    return {
        "folder": data_folder,
        "label": folder_name,
        "ky": ky_sorted,
        "avg": avg_sorted,
        "summary_csv": summary_csv,
        "bad_files": bad_files,
    }


# -----------------------------
# Main
# -----------------------------
def main():
    roi_w = ask_positive_int("Enter ROI width in pixels (e.g. 20): ")
    roi_h = ask_positive_int("Enter ROI height in pixels (e.g. 50): ")

    results = []
    for data_folder in DATA_FOLDERS:
        result = process_folder(
            data_folder,
            roi_w=roi_w,
            roi_h=roi_h,
            positive_only=PLOT_ONLY_POSITIVE_KY,
        )
        results.append(result)

    common_parent = os.path.dirname(os.path.normpath(DATA_FOLDERS[0]))
    plot_png = os.path.join(common_parent, "comparison_avg_counts_vs_ky_positive_only.png")

    plt.figure(figsize=(7.5, 4.8))
    for result in results:
        plt.plot(result["ky"], result["avg"], marker="o", linestyle="-", label=result["label"])

    plt.xlabel("ky")
    plt.ylabel("Average counts")
    plt.title("Average counts vs positive ky")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(plot_png, dpi=150)
    plt.show()

    print("Comparison plot saved to:")
    print(plot_png)

    for result in results:
        print(f"\nFolder: {result['folder']}")
        print(f"Summary CSV: {result['summary_csv']}")
        print("Processed files (ky -> average counts):")
        for ky, avg in zip(result["ky"], result["avg"]):
            print(f"{ky:+0.3f} -> {avg:.3f}")

        if result["bad_files"]:
            print("Skipped files:")
            for file_name, message in result["bad_files"]:
                print(f"- {file_name}: {message}")


if __name__ == "__main__":
    main()