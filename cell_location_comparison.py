import numpy as np
from PIL import Image
import os
import shutil

# Parse line to get coordinates and dimensions of bounding box.
def parse_line(line):
    items = list(map(float, line.split()[1:]))  # Ignore class_id
    return np.array(items)

# Convert normalized box coordinates to pixel coordinates.
def box_to_pixel(box, image_width, image_height):
    x_center, y_center, width, height = box
    x_center *= image_width
    y_center *= image_height
    width *= image_width
    height *= image_height
    left = x_center - width / 2
    top = y_center - height / 2
    right = x_center + width / 2
    bottom = y_center + height / 2
    return [int(val) for val in [left, top, right, bottom]]

def compare_txts_and_crop(file1, file2, image1_path, image2_path, output_dir1, output_dir2, threshold=0.01):
    with open(file1, 'r') as f1, open(file2, 'r') as f2:
        lines1 = [parse_line(line) for line in f1.readlines()]
        lines2 = [parse_line(line) for line in f2.readlines()]

        image1 = Image.open(image1_path)
        image2 = Image.open(image2_path)

        os.makedirs(output_dir1, exist_ok=True)
        os.makedirs(output_dir2, exist_ok=True)

        for i, box1 in enumerate(lines1):
            for j, box2 in enumerate(lines2):
                # Check if the boxes match within the threshold
                if np.allclose(box1, box2, atol=threshold):
                    # Crop and save the matched regions
                    box1_pixel = box_to_pixel(box1, image1.width, image1.height)
                    output_file1 = get_unique_filename(output_dir1, f"crop_{i}_{j}.jpg")
                    crop1 = image1.crop(box1_pixel)
                    crop1.save(output_file1)

                    box2_pixel = box_to_pixel(box2, image2.width, image2.height)
                    output_file2 = get_unique_filename(output_dir2, f"crop_{i}_{j}.jpg")
                    crop2 = image2.crop(box2_pixel)
                    crop2.save(output_file2)

                    # Remove the matched box from lines2 to avoid matching it again
                    del lines2[j]
                    break  # Exit the loop if a match is found

# Get a unique file name by appending a number to the base name
def get_unique_filename(directory, base_name):
    filename, extension = os.path.splitext(base_name)
    counter = 1
    while os.path.exists(os.path.join(directory, base_name)):
        base_name = f"{filename}_{counter}{extension}"
        counter += 1
    return os.path.join(directory, base_name)

# Create output directories
output_dir1 = r"C:\example_path\processed_images_BF"
output_dir2 = r"C:\example_path\processed_images_AF"
os.makedirs(output_dir1, exist_ok=True)
os.makedirs(output_dir2, exist_ok=True)

# Use the function
for i in range(1, 119):  # Range of files
    # Text file paths
    txt_dir1 = rf"C:\example_path\labels_BF\{i}.txt"
    txt_dir2 = rf"C:\example_path\labels_AF\{i}.txt"
    if not os.path.exists(txt_dir1) or not os.path.exists(txt_dir2):
        continue
    # Image paths
    image_dir1 = rf"C:\example_path\images_BF\{i}.jpg"
    image_dir2 = rf"C:\example_path\images_AF\{i}.jpg"
    if not os.path.exists(image_dir1) or not os.path.exists(image_dir2):
        continue
    output_subdir1 = os.path.join(output_dir1, f"processed_BF_{i}")
    output_subdir2 = os.path.join(output_dir2, f"processed_AF_{i}")
    compare_txts_and_crop(txt_dir1, txt_dir2, image_dir1, image_dir2, output_subdir1, output_subdir2)

print("All files processed and saved in the output directory.")

# Move images from BF_combined to BF_final directory
target_directory = r"C:\example_path\final_BF"
os.makedirs(target_directory, exist_ok=True)
existing_files = set()  # Set to keep track of existing file names

for subdir in os.listdir(output_dir1):
    subdir_path = os.path.join(output_dir1, subdir)
    if os.path.isdir(subdir_path):
        for filename in os.listdir(subdir_path):
            if filename.endswith(".jpg"):
                src_path = os.path.join(subdir_path, filename)
                dst_path = os.path.join(target_directory, filename)
                if filename in existing_files:
                    # Generate a new unique file name
                    base_name, extension = os.path.splitext(filename)
                    counter = 1
                    while os.path.exists(os.path.join(target_directory, f"{base_name}_{counter}{extension}")):
                        counter += 1
                    dst_path = os.path.join(target_directory, f"{base_name}_{counter}{extension}")
                existing_files.add(os.path.basename(dst_path))
                shutil.move(src_path, dst_path)

# Move images from AF_combined to AF_final directory
target_directory = r"C:\example_path\final_AF"
os.makedirs(target_directory, exist_ok=True)
existing_files = set()  # Set to keep track of existing file names

for subdir in os.listdir(output_dir2):
    subdir_path = os.path.join(output_dir2, subdir)
    if os.path.isdir(subdir_path):
        for filename in os.listdir(subdir_path):
            if filename.endswith(".jpg"):
                src_path = os.path.join(subdir_path, filename)
                dst_path = os.path.join(target_directory, filename)
                if filename in existing_files:
                    # Generate a new unique file name
                    base_name, extension = os.path.splitext(filename)
                    counter = 1
                    while os.path.exists(os.path.join(target_directory, f"{base_name}_{counter}{extension}")):
                        counter += 1
                    dst_path = os.path.join(target_directory, f"{base_name}_{counter}{extension}")
                existing_files.add(os.path.basename(dst_path))
                shutil.move(src_path, dst_path)

# Delete the combined directories
shutil.rmtree(output_dir1)
shutil.rmtree(output_dir2)
