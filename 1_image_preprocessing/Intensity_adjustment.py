"""
Image Brightness Normalization and CLAHE Enhancement

This script:
1. Calculates the global average brightness of input grayscale images.
2. Normalizes each image to match the global average brightness.
3. Applies CLAHE (Contrast Limited Adaptive Histogram Equalization).
4. Saves the enhanced images to an output folder.

Dependencies: OpenCV (cv2), tqdm, os
"""

import cv2
import os
from tqdm import tqdm

# Input/output folders
input_folder = "./input_images"
output_folder = "./output_images"
os.makedirs(output_folder, exist_ok=True)

# CLAHE processor
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

# Image list
file_list = [f for f in os.listdir(input_folder) if f.lower().endswith(('.jpg', '.png'))]

# Global average brightness
total_brightness = 0
valid_images = 0
for f in file_list:
    img = cv2.imread(os.path.join(input_folder, f))
    if img is not None:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        total_brightness += cv2.mean(gray)[0]
        valid_images += 1
if valid_images == 0:
    raise RuntimeError("No valid images found.")
global_mean = total_brightness / valid_images

# Process images
for fname in tqdm(file_list, desc="Processing"):
    img = cv2.imread(os.path.join(input_folder, fname))
    if img is None:
        continue
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    local_mean = cv2.mean(gray)[0]
    alpha = global_mean / local_mean if local_mean != 0 else 1.0
    normalized = cv2.convertScaleAbs(gray, alpha=alpha)
    enhanced = clahe.apply(normalized)
    cv2.imwrite(os.path.join(output_folder, fname), enhanced)
