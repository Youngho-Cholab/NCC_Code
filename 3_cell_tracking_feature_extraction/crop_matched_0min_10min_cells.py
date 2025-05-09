"""
This script crops matched single-cell regions from paired BF and AF images using YOLO-generated bounding boxes.

Prerequisites:
- Run YOLO detection first to generate label `.txt` files (YOLO format) in labels/BF and labels/AF:
  <class_id> <x_center> <y_center> <width> <height> (all normalized)
- Place the corresponding raw BF and AF images (unboxed) in images/BF and images/AF.
- Label and image filenames must match (e.g., 001.txt ↔ 001.jpg)

Output:
- Cropped single-cell images saved in cropped/BF and cropped/AF.
"""

import numpy as np
from PIL import Image
import os
import shutil

# Parse YOLO label line to numpy array (ignore class_id)
def parse_line(line):
    return np.array(list(map(float, line.strip().split()[1:])))

# Get box center coordinates
def get_center(box):
    return np.array([box[0], box[1]])

# Convert normalized box to pixel coordinates
def box_to_pixel(box, image_width, image_height):
    x, y, w, h = box
    x *= image_width
    y *= image_height
    w *= image_width
    h *= image_height
    return [x - w / 2, y - h / 2, x + w / 2, y + h / 2]

# Check if crop box is mostly out of bounds
def box_out_of_bounds(box, img_w, img_h):
    l, t, r, b = box
    box_area = max(r - l, 1) * max(b - t, 1)
    clipped_l = max(l, 0)
    clipped_t = max(t, 0)
    clipped_r = min(r, img_w)
    clipped_b = min(b, img_h)
    clipped_area = max(clipped_r - clipped_l, 0) * max(clipped_b - clipped_t, 0)

    lost_ratio = 1 - (clipped_area / box_area)
    center_x = (l + r) / 2
    center_y = (t + b) / 2
    center_inside = (0 <= center_x <= img_w) and (0 <= center_y <= img_h)

    if lost_ratio <= 0.2:
        return False
    elif lost_ratio <= 0.3:
        return not center_inside
    return True

# Save with unique name to avoid overwrite
def get_unique_filename(folder, base_name):
    name, ext = os.path.splitext(base_name)
    i = 1
    path = os.path.join(folder, base_name)
    while os.path.exists(path):
        path = os.path.join(folder, f"{name}_{i}{ext}")
        i += 1
    return path

# Match BF–AF labels and crop corresponding cells
def compare_txts_and_crop(txt_bf, txt_af, img_bf, img_af, out_bf, out_af, threshold=0.01):
    with open(txt_bf) as f1, open(txt_af) as f2:
        boxes_bf = [parse_line(l) for l in f1]
        boxes_af = [parse_line(l) for l in f2]

    image_bf = Image.open(img_bf)
    image_af = Image.open(img_af)
    w_bf, h_bf = image_bf.size
    w_af, h_af = image_af.size

    os.makedirs(out_bf, exist_ok=True)
    os.makedirs(out_af, exist_ok=True)

    used = set()
    for i, box1 in enumerate(boxes_bf):
        dists = [np.linalg.norm(get_center(box1) - get_center(box2)) if j not in used else float("inf")
                 for j, box2 in enumerate(boxes_af)]
        best_j = int(np.argmin(dists))
        if dists[best_j] >= threshold:
            continue
        used.add(best_j)

        pix1 = box_to_pixel(box1, w_bf, h_bf)
        pix2 = box_to_pixel(boxes_af[best_j], w_af, h_af)

        if box_out_of_bounds(pix1, w_bf, h_bf) or box_out_of_bounds(pix2, w_af, h_af):
            continue

        crop1 = image_bf.crop([int(c) for c in pix1])
        crop2 = image_af.crop([int(c) for c in pix2])

        name = f"cell_{i}_{best_j}.jpg"
        crop1.save(get_unique_filename(out_bf, name))
        crop2.save(get_unique_filename(out_af, name))

# === Example Execution ===
if __name__ == "__main__":
    # === User-defined paths ===
    bf_label_folder = "labels/BF"
    af_label_folder = "labels/AF"
    bf_image_folder = "images/BF"
    af_image_folder = "images/AF"
    output_dir_bf = "cropped/BF"
    output_dir_af = "cropped/AF"
    image_ext = ".jpg"

    # === Process starts ===
    os.makedirs(output_dir_bf, exist_ok=True)
    os.makedirs(output_dir_af, exist_ok=True)

    bf_ids = {os.path.splitext(f)[0] for f in os.listdir(bf_label_folder) if f.endswith(".txt")}
    af_ids = {os.path.splitext(f)[0] for f in os.listdir(af_label_folder) if f.endswith(".txt")}
    common_ids = sorted(bf_ids & af_ids)

    for img_id in common_ids:
        txt_bf = os.path.join(bf_label_folder, f"{img_id}.txt")
        txt_af = os.path.join(af_label_folder, f"{img_id}.txt")
        img_bf = os.path.join(bf_image_folder, f"{img_id}{image_ext}")
        img_af = os.path.join(af_image_folder, f"{img_id}{image_ext}")
        if not (os.path.exists(txt_bf) and os.path.exists(txt_af) and os.path.exists(img_bf) and os.path.exists(img_af)):
            continue
        compare_txts_and_crop(txt_bf, txt_af, img_bf, img_af, output_dir_bf, output_dir_af)