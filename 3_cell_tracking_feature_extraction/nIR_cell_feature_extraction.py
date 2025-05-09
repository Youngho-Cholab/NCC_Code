"""
This script performs single-cell analysis on YOLO-cropped brightfield (BF) and autofluorescence (AF) images.
It extracts morphological parameters (major/minor axis, area, eccentricity), calculates FWHM from intensity profiles,
and computes molecular properties such as intracellular H2O2 concentration, efflux rate, and refractive index.

Required:
  - Input image directories: crops/BF and crops/AF
  - These images must be generated using crop_yolo_matched_cells.py (bounding box-based cell matching)
"""
  
import os
import cv2
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
from math import pi, sqrt

# === Step 1: Image Analysis ===

# Input and output directories
bf_dir = "crops/BF"
af_dir = "crops/AF"
bf_save_dir = "output/BF"
af_save_dir = "output/AF"
os.makedirs(bf_save_dir, exist_ok=True)
os.makedirs(af_save_dir, exist_ok=True)

# Initialize dataframe to store results
data = pd.DataFrame(columns=[
    "Filename", "Major Axis", "Minor Axis", "Size(μm²)", "Eccentricity",
    "FWHM", "Intensity Mean (First Image)", "Intensity Mean (Second Image)"
])

# Process all images
for fname in os.listdir(bf_dir):
    if not fname.endswith(".jpg"):
        continue

    bf_path = os.path.join(bf_dir, fname)
    af_path = os.path.join(af_dir, fname.replace("BF", "AF"))
    src_bf = cv2.imread(bf_path, cv2.IMREAD_GRAYSCALE)
    src_af = cv2.imread(af_path, cv2.IMREAD_GRAYSCALE)
    if src_bf is None or src_af is None:
        continue

    # Normalize brightness
    src_bf_adj = np.clip(src_bf + (80 - np.mean(src_bf)), 0, 255).astype(np.uint8)

    # Find best ellipse by contrast-threshold scanning
    best_ellipse, best_ecc = None, float("inf")
    for alpha in np.arange(1.0, 5.0, 0.2):
        for th in range(80, 128, 4):
            adjusted = np.clip((1 + alpha) * src_bf_adj - 128 * alpha, 0, 255).astype(np.uint8)
            _, binary = cv2.threshold(adjusted, th, 255, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            for cnt in contours:
                if len(cnt) < 5:
                    continue
                ellipse = cv2.fitEllipse(cnt)
                (_, axes, _) = ellipse
                major, minor = max(axes), min(axes)
                ecc = sqrt(1 - (minor / major) ** 2)
                if 5 <= minor <= 13 and ecc < best_ecc:
                    best_ellipse, best_ecc = ellipse, ecc

    if best_ellipse is None:
        continue

    # Extract ellipse-based features
    center, axes, angle = best_ellipse
    major, minor = max(axes), min(axes)
    area = pi * (major / 2) * (minor / 2)
    scale = 1.497
    eccentricity = sqrt(1 - (minor / major) ** 2)

    # Mask-based intensity calculation
    mask = np.zeros_like(src_bf)
    cv2.ellipse(mask, best_ellipse, 255, -1)
    intensity_bf = np.mean(src_bf[mask == 255]) / 255.0
    intensity_af = np.mean(src_af[mask == 255]) / 255.0

    # FWHM along minor axis
    short_r = min(axes) / 2
    x_vals = range(int(center[1] - short_r), int(center[1] + short_r))
    y_profile = [
        np.mean(src_bf[y, max(0, int(center[0] - short_r)):min(src_bf.shape[1], int(center[0] + short_r))])
        if 0 <= y < src_bf.shape[0] else 0 for y in x_vals
    ]
    y_norm = (np.array(y_profile) - min(y_profile)) / (max(y_profile) - min(y_profile) + 1e-8)
    max_idx = np.argmax(y_norm)
    try:
        fwhm = abs(
            interp1d(y_norm[:max_idx + 1], x_vals[:max_idx + 1])(0.5) -
            interp1d(y_norm[max_idx:], x_vals[max_idx:])(0.5)
        )
    except:
        continue

    # Append results
    data.loc[len(data)] = [
        fname, major * scale, minor * scale, area * scale**2,
        eccentricity, fwhm, intensity_bf, intensity_af
    ]

    # Draw ellipse and save
    ellipse_draw = (center, (axes[0]+4, axes[1]+4), angle)
    cv2.ellipse(cv2.cvtColor(src_bf, cv2.COLOR_GRAY2BGR), ellipse_draw, (0, 255, 0), 1)
    cv2.ellipse(cv2.cvtColor(src_af, cv2.COLOR_GRAY2BGR), ellipse_draw, (0, 255, 0), 1)
    cv2.imwrite(os.path.join(bf_save_dir, fname), src_bf)
    cv2.imwrite(os.path.join(af_save_dir, fname), src_af)

# Save to Excel
excel_path = "cell_analysis_results.xlsx"
data.to_excel(excel_path, index=False)

# === Step 2: Molecular Calculations ===

# Load saved result
df = pd.read_excel(excel_path)
mid_path = "cell_analysis_results_M.xlsx"
final_path = "cell_analysis_results_MR.xlsx"

# Calculate concentration and efflux rate per cell
df['H₂O₂_sensor(M)'] = (df.iloc[:, 6] * 0.00204 / df.iloc[:, 7]) - 0.00204
df['H₂O₂_cell(M)'] = df['H₂O₂_sensor(M)'] / 0.193
df['H₂O₂_cell(μM)'] = df['H₂O₂_cell(M)'] * 1000
df['cell volume(µm³)'] = (4 / 3) * pi * (df["Major Axis"]/2) * (df["Minor Axis"]/2) * ((df["Major Axis"] + df["Minor Axis"]) / 4)
df['H₂O₂ efflux rate [femtomole·cell⁻¹min⁻¹]'] = df['cell volume(µm³)'] * 1e-15 * df['H₂O₂_cell(M)'] * 1e15 / 10
df.to_excel(mid_path, index=False)

# Calculate refractive index
# This formula was derived based on optical simulation results (FDTD-based model)
radius = np.sqrt(df['Eccentricity'] / pi)
intensity = df['FWHM']
df['Refractive index [n]'] = (
    1.613 + 0.057 * radius + 0.503 * np.log(radius) + 0.114 * np.log(intensity) +
    0.334 / radius + 0.178 / intensity + 0.012 * (radius / intensity) -
    0.015 * (intensity / radius) - 0.673 * np.sqrt(radius) - 0.060 * np.sqrt(intensity)
)

# Save final output
df.to_excel(final_path, index=False)
