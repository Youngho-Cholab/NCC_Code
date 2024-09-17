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
            # matched = False  # Flag to check if a match was found
            for j, box2 in enumerate(lines2):
                # Check if the boxes match within the threshold
                if np.allclose(box1, box2, atol=threshold):
                    # matched = True
                    # Crop and save the matched regions
                    box1_pixel = box_to_pixel(box1, image1.width, image1.height)
                    output_file1 = get_unique_filename(output_dir1, f"crop_{i}_{j}.jpg")  # Get a unique file name
                    crop1 = image1.crop(box1_pixel)
                    crop1.save(output_file1)

                    box2_pixel = box_to_pixel(box2, image2.width, image2.height)
                    output_file2 = get_unique_filename(output_dir2, f"crop_{i}_{j}.jpg")  # Get a unique file name
                    crop2 = image2.crop(box2_pixel)
                    crop2.save(output_file2)

                    # Remove the matched box from lines2 to avoid matching it again
                    del lines2[j]
                    break  # Exit the loop if a match is found

        #     if not matched:
        #         print(f"No match found for the box {i} in file1.")

        # print("Done.")

# Get a unique file name by appending a number to the base name
def get_unique_filename(directory, base_name):
    filename, extension = os.path.splitext(base_name)
    counter = 1
    while os.path.exists(os.path.join(directory, base_name)):
        base_name = f"{filename}_{counter}{extension}"
        counter += 1
    return os.path.join(directory, base_name)

########## 파일명

# -------------24.01.25_ADSC_D15_START----------------

# Create output directory
# 1. 파일명 변경 (2)
output_dir1 = r"C:\ADSC_data\Python_image_process\ADSC_BF_combined"
output_dir2 = r"C:\ADSC_data\Python_image_process\ADSC_AF_combined"
os.makedirs(output_dir1, exist_ok=True)
os.makedirs(output_dir2, exist_ok=True)

# Use the function
# 2. 파일 경로 변경 필요 항상 BF먼저 이후 AF. (범위 변경 필요) (6+ 범위)
for i in range(1, 105): #range(start, stop) 함수에서 stop의 값은 범위에 포함되지 않는다
    #location txt file
    txt_dir1 = rf"C:\ADSC_data\ADSC_D1\Deep_ADSC_O1_24.06.05_BF\labels\{i}.txt"
    txt_dir2 = rf"C:\ADSC_data\ADSC_D1\Deep_ADSC_O1_24.06.05_AF\labels\{i}.txt"
    if not os.path.exists(txt_dir1) or not os.path.exists(txt_dir2): continue
    #orginal image
    image_dir1 = rf"C:\ADSC_data\ADSC_D1\EF_ADSC_O1_24.06.05_BF\{i}.jpg"
    image_dir2 = rf"C:\ADSC_data\ADSC_D1\EF_ADSC_O1_24.06.05_AF\{i}.jpg"
    if not os.path.exists(image_dir1) or not os.path.exists(image_dir2): continue
    output_subdir1 = os.path.join(output_dir1, f"24.06.05_ADSC_O1_BF_{i}")
    output_subdir2 = os.path.join(output_dir2, f"24.06.05_ADSC_O1_AF_{i}")
    compare_txts_and_crop(txt_dir1, txt_dir2, image_dir1, image_dir2, output_subdir1, output_subdir2)

print("All files processed and saved in the output directory.")

# Move images from hDF_P15_BF_combined to hDF_P15_BF directory
# 3. 파일 이름명 변경 필요 (1)
target_directory = r"C:\ADSC_data\ADSC_D1\ADSC_O1_24.06.05_BF"
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
                    while os.path.exists(os.path.join(target_directory , f"{base_name}_{counter}{extension}")):
                        counter += 1
                    dst_path = os.path.join(target_directory , f"{base_name}_{counter}{extension}")
                existing_files.add(os.path.basename(dst_path))
                shutil.move(src_path, dst_path)

# Move images from hDF_P15_AF_combined to hDF_P15_AF directory
# 4. 파일 이름명 변경 필요 (1)
target_directory = r"C:\ADSC_data\ADSC_D1\ADSC_O1_24.06.05_AF"
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
                    while os.path.exists(os.path.join(target_directory , f"{base_name}_{counter}{extension}")):
                        counter += 1
                    dst_path = os.path.join(target_directory , f"{base_name}_{counter}{extension}")
                existing_files.add(os.path.basename(dst_path))
                shutil.move(src_path, dst_path)

print("Images moved to respective directories.")

# Delete the hDF_P15_AF_combined directory

shutil.rmtree(output_dir1)
shutil.rmtree(output_dir2)

print("-------------ADSC_D1")

# -------------24.01.25_ADSC_D15_START----------------

# Create output directory
# 1. 파일명 변경 (2)
output_dir1 = r"C:\ADSC_data\Python_image_process\ADSC_BF_combined"
output_dir2 = r"C:\ADSC_data\Python_image_process\ADSC_AF_combined"
os.makedirs(output_dir1, exist_ok=True)
os.makedirs(output_dir2, exist_ok=True)

# Use the function
# 2. 파일 경로 변경 필요 항상 BF먼저 이후 AF. (범위 변경 필요) (6+ 범위)
for i in range(1, 119): #range(start, stop) 함수에서 stop의 값은 범위에 포함되지 않는다
    #location txt file
    txt_dir1 = rf"C:\ADSC_data\ADSC_D7\Deep_ADSC_O7_24.06.11_BF\labels\{i}.txt"
    txt_dir2 = rf"C:\ADSC_data\ADSC_D7\Deep_ADSC_O7_24.06.11_AF\labels\{i}.txt"
    if not os.path.exists(txt_dir1) or not os.path.exists(txt_dir2): continue
    #orginal image
    image_dir1 = rf"C:\ADSC_data\ADSC_D7\EF_ADSC_O7_24.06.11_BF\{i}.jpg"
    image_dir2 = rf"C:\ADSC_data\ADSC_D7\EF_ADSC_O7_24.06.11_AF\{i}.jpg"
    if not os.path.exists(image_dir1) or not os.path.exists(image_dir2): continue
    output_subdir1 = os.path.join(output_dir1, f"24.06.11_ADSC_O7_BF_{i}")
    output_subdir2 = os.path.join(output_dir2, f"24.06.11_ADSC_O7_AF_{i}")
    compare_txts_and_crop(txt_dir1, txt_dir2, image_dir1, image_dir2, output_subdir1, output_subdir2)

print("All files processed and saved in the output directory.")

# Move images from hDF_P15_BF_combined to hDF_P15_BF directory
# 3. 파일 이름명 변경 필요 (1)
target_directory = r"C:\ADSC_data\ADSC_D7\ADSC_O7_24.06.11_BF"
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
                    while os.path.exists(os.path.join(target_directory , f"{base_name}_{counter}{extension}")):
                        counter += 1
                    dst_path = os.path.join(target_directory , f"{base_name}_{counter}{extension}")
                existing_files.add(os.path.basename(dst_path))
                shutil.move(src_path, dst_path)

# Move images from hDF_P15_AF_combined to hDF_P15_AF directory
# 4. 파일 이름명 변경 필요 (1)
target_directory = r"C:\ADSC_data\ADSC_D7\ADSC_O7_24.06.11_AF"
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
                    while os.path.exists(os.path.join(target_directory , f"{base_name}_{counter}{extension}")):
                        counter += 1
                    dst_path = os.path.join(target_directory , f"{base_name}_{counter}{extension}")
                existing_files.add(os.path.basename(dst_path))
                shutil.move(src_path, dst_path)

print("Images moved to respective directories.")

# Delete the hDF_P15_AF_combined directory

shutil.rmtree(output_dir1)
shutil.rmtree(output_dir2)

print("-------------ADSC_D7")


# -------------24.01.25_ADSC_D15_START----------------

# Create output directory
# 1. 파일명 변경 (2)
output_dir1 = r"C:\ADSC_data\Python_image_process\ADSC_BF_combined"
output_dir2 = r"C:\ADSC_data\Python_image_process\ADSC_AF_combined"
os.makedirs(output_dir1, exist_ok=True)
os.makedirs(output_dir2, exist_ok=True)

# Use the function
# 2. 파일 경로 변경 필요 항상 BF먼저 이후 AF. (범위 변경 필요) (6+ 범위)
for i in range(1, 84): #range(start, stop) 함수에서 stop의 값은 범위에 포함되지 않는다
    #location txt file
    txt_dir1 = rf"C:\ADSC_data\ADSC_D15\Deep_ADSC_O15_24.06.19_BF\labels\{i}.txt"
    txt_dir2 = rf"C:\ADSC_data\ADSC_D15\Deep_ADSC_O15_24.06.19_AF\labels\{i}.txt"
    if not os.path.exists(txt_dir1) or not os.path.exists(txt_dir2): continue
    #orginal image
    image_dir1 = rf"C:\ADSC_data\ADSC_D15\EF_ADSC_O15_24.06.19_BF\{i}.jpg"
    image_dir2 = rf"C:\ADSC_data\ADSC_D15\EF_ADSC_O15_24.06.19_AF\{i}.jpg"
    if not os.path.exists(image_dir1) or not os.path.exists(image_dir2): continue
    output_subdir1 = os.path.join(output_dir1, f"24.06.19_ADSC_O7_BF_{i}")
    output_subdir2 = os.path.join(output_dir2, f"24.06.19_ADSC_O7_AF_{i}")
    compare_txts_and_crop(txt_dir1, txt_dir2, image_dir1, image_dir2, output_subdir1, output_subdir2)

print("All files processed and saved in the output directory.")

# Move images from hDF_P15_BF_combined to hDF_P15_BF directory
# 3. 파일 이름명 변경 필요 (1)
target_directory = r"C:\ADSC_data\ADSC_D15\ADSC_O15_24.06.19_BF"
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
                    while os.path.exists(os.path.join(target_directory , f"{base_name}_{counter}{extension}")):
                        counter += 1
                    dst_path = os.path.join(target_directory , f"{base_name}_{counter}{extension}")
                existing_files.add(os.path.basename(dst_path))
                shutil.move(src_path, dst_path)

# Move images from hDF_P15_AF_combined to hDF_P15_AF directory
# 4. 파일 이름명 변경 필요 (1)
target_directory = r"C:\ADSC_data\ADSC_D15\ADSC_O15_24.06.19_AF"
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
                    while os.path.exists(os.path.join(target_directory , f"{base_name}_{counter}{extension}")):
                        counter += 1
                    dst_path = os.path.join(target_directory , f"{base_name}_{counter}{extension}")
                existing_files.add(os.path.basename(dst_path))
                shutil.move(src_path, dst_path)

print("Images moved to respective directories.")

# Delete the hDF_P15_AF_combined directory

shutil.rmtree(output_dir1)
shutil.rmtree(output_dir2)

print("-------------ADSC_D15")

# -------------24.01.25_ADSC_D15_START----------------

# Create output directory
# 1. 파일명 변경 (2)
output_dir1 = r"C:\ADSC_data\Python_image_process\ADSC_BF_combined"
output_dir2 = r"C:\ADSC_data\Python_image_process\ADSC_AF_combined"
os.makedirs(output_dir1, exist_ok=True)
os.makedirs(output_dir2, exist_ok=True)

# Use the function
# 2. 파일 경로 변경 필요 항상 BF먼저 이후 AF. (범위 변경 필요) (6+ 범위)
for i in range(1, 82): #range(start, stop) 함수에서 stop의 값은 범위에 포함되지 않는다
    #location txt file
    txt_dir1 = rf"C:\ADSC_data\ADSC_D21\Deep_ADSC_O21_24.06.25_BF\labels\{i}.txt"
    txt_dir2 = rf"C:\ADSC_data\ADSC_D21\Deep_ADSC_O21_24.06.25_AF\labels\{i}.txt"
    if not os.path.exists(txt_dir1) or not os.path.exists(txt_dir2): continue
    #orginal image
    image_dir1 = rf"C:\ADSC_data\ADSC_D21\EF_ADSC_O21_24.06.25_BF\{i}.jpg"
    image_dir2 = rf"C:\ADSC_data\ADSC_D21\EF_ADSC_O21_24.06.25_AF\{i}.jpg"
    if not os.path.exists(image_dir1) or not os.path.exists(image_dir2): continue
    output_subdir1 = os.path.join(output_dir1, f"24.06.25_ADSC_O21_BF_{i}")
    output_subdir2 = os.path.join(output_dir2, f"24.06.25_ADSC_O21_AF_{i}")
    compare_txts_and_crop(txt_dir1, txt_dir2, image_dir1, image_dir2, output_subdir1, output_subdir2)

print("All files processed and saved in the output directory.")

# Move images from hDF_P15_BF_combined to hDF_P15_BF directory
# 3. 파일 이름명 변경 필요 (1)
target_directory = r"C:\ADSC_data\ADSC_D21\ADSC_O21_24.06.25_BF"
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
                    while os.path.exists(os.path.join(target_directory , f"{base_name}_{counter}{extension}")):
                        counter += 1
                    dst_path = os.path.join(target_directory , f"{base_name}_{counter}{extension}")
                existing_files.add(os.path.basename(dst_path))
                shutil.move(src_path, dst_path)

# Move images from hDF_P15_AF_combined to hDF_P15_AF directory
# 4. 파일 이름명 변경 필요 (1)
target_directory = r"C:\ADSC_data\ADSC_D21\ADSC_O21_24.06.25_AF"
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
                    while os.path.exists(os.path.join(target_directory , f"{base_name}_{counter}{extension}")):
                        counter += 1
                    dst_path = os.path.join(target_directory , f"{base_name}_{counter}{extension}")
                existing_files.add(os.path.basename(dst_path))
                shutil.move(src_path, dst_path)

print("Images moved to respective directories.")

# Delete the hDF_P15_AF_combined directory

shutil.rmtree(output_dir1)
shutil.rmtree(output_dir2)

print("-------------ADSC_D21")

# # -------------23.06.06_hDF_P9_START----------------

# # Create output directory
# # 1. 파일명 변경 (2)
# output_dir1 = "D:\\Cell_location\\hDF_P13_BF_combined"
# output_dir2 = "D:\\Cell_location\\hDF_P13_AF_combined"
# os.makedirs(output_dir1, exist_ok=True)
# os.makedirs(output_dir2, exist_ok=True)

# # Use the function
# # 2. 파일 경로 변경 필요 항상 BF먼저 이후 AF. (범위 변경 필요) (6+ 범위)
# for i in range(1, 183): #range(start, stop) 함수에서 stop의 값은 범위에 포함되지 않는다
#     txt_dir1 = rf"D:\YH_23.08.07_backup\7.20hDF_P13_BF\labels\{i}.txt"
#     txt_dir2 = rf"D:\YH_23.08.07_backup\7.20hDF_P13_AF\labels\{i}.txt"
#     if not os.path.exists(txt_dir1) or not os.path.exists(txt_dir2): continue
#     image_dir1 = rf"D:\YH_23.08.07_backup\23.07.20\hDF_P13_BF\{i}.jpg"
#     image_dir2 = rf"D:\YH_23.08.07_backup\23.07.20\hDF_P13_AF\{i}.jpg"
#     if not os.path.exists(image_dir1) or not os.path.exists(image_dir2): continue
#     output_subdir1 = os.path.join(output_dir1, f"23.07.20_hDF_P13_BF_{i}")
#     output_subdir2 = os.path.join(output_dir2, f"23.07.20_hDF_P13_AF_{i}")
#     compare_txts_and_crop(txt_dir1, txt_dir2, image_dir1, image_dir2, output_subdir1, output_subdir2)

# print("All files processed and saved in the output directory.")


# # Move images from hDF_P15_BF_combined to hDF_P15_BF directory
# # 3. 파일 이름명 변경 필요 (1)
# target_directory = "D:\\Cell_location\\23.07.20_hDF_P13_BF"  
# os.makedirs(target_directory, exist_ok=True)
# existing_files = set()  # Set to keep track of existing file names

# for subdir in os.listdir(output_dir1):
#     subdir_path = os.path.join(output_dir1, subdir)
#     if os.path.isdir(subdir_path):
#         for filename in os.listdir(subdir_path):
#             if filename.endswith(".jpg"):
#                 src_path = os.path.join(subdir_path, filename)
#                 dst_path = os.path.join(target_directory, filename)
#                 if filename in existing_files:
#                     # Generate a new unique file name
#                     base_name, extension = os.path.splitext(filename)
#                     counter = 1
#                     while os.path.exists(os.path.join(target_directory , f"{base_name}_{counter}{extension}")):
#                         counter += 1
#                     dst_path = os.path.join(target_directory , f"{base_name}_{counter}{extension}")
#                 existing_files.add(os.path.basename(dst_path))
#                 shutil.move(src_path, dst_path)

# # Move images from hDF_P15_AF_combined to hDF_P15_AF directory
# # 4. 파일 이름명 변경 필요 (1)
# target_directory = "D:\\Cell_location\\23.07.20_hDF_P13_AF"  
# os.makedirs(target_directory, exist_ok=True)
# existing_files = set()  # Set to keep track of existing file names

# for subdir in os.listdir(output_dir2):
#     subdir_path = os.path.join(output_dir2, subdir)
#     if os.path.isdir(subdir_path):
#         for filename in os.listdir(subdir_path):
#             if filename.endswith(".jpg"):
#                 src_path = os.path.join(subdir_path, filename)
#                 dst_path = os.path.join(target_directory, filename)
#                 if filename in existing_files:
#                     # Generate a new unique file name
#                     base_name, extension = os.path.splitext(filename)
#                     counter = 1
#                     while os.path.exists(os.path.join(target_directory , f"{base_name}_{counter}{extension}")):
#                         counter += 1
#                     dst_path = os.path.join(target_directory , f"{base_name}_{counter}{extension}")
#                 existing_files.add(os.path.basename(dst_path))
#                 shutil.move(src_path, dst_path)

# print("Images moved to respective directories.")

# # Delete the hDF_P15_AF_combined directory

# shutil.rmtree(output_dir1)
# shutil.rmtree(output_dir2)

# print("-------------23.07.20_hDF_P13_END.")

# # -------------23.05.27_hDF_P7_START----------------

# # Create output directory
# # 1. 파일명 변경 (2)
# output_dir1 = "D:\\Cell_location\\hDF_P7_BF_combined"
# output_dir2 = "D:\\Cell_location\\hDF_P7_AF_combined"
# os.makedirs(output_dir1, exist_ok=True)
# os.makedirs(output_dir2, exist_ok=True)

# # Use the function
# # 2. 파일 경로 변경 필요 항상 BF먼저 이후 AF. (범위 변경 필요) (6+ 범위)
# for i in range(1, 79): #range(start, stop) 함수에서 stop의 값은 범위에 포함되지 않는다
#     txt_dir1 = rf"D:\deep learning\23.05.27hDF_P7_BFj\labels\{i}.txt"
#     txt_dir2 = rf"D:\deep learning\23.05.27hDF_P7_AFj\labels\{i}.txt"
#     if not os.path.exists(txt_dir1) or not os.path.exists(txt_dir2): continue
#     image_dir1 = rf"D:\YH_23.06.07_backup\23.05.27\hDF_P7_BF\{i}.jpg"
#     image_dir2 = rf"D:\YH_23.06.07_backup\23.05.27\hDF_P7_AF\{i}.jpg"
#     if not os.path.exists(image_dir1) or not os.path.exists(image_dir2): continue
#     output_subdir1 = os.path.join(output_dir1, f"23.05.27_hDF_P7_BF_{i}")
#     output_subdir2 = os.path.join(output_dir2, f"23.05.27_hDF_P7_AF_{i}")
#     compare_txts_and_crop(txt_dir1, txt_dir2, image_dir1, image_dir2, output_subdir1, output_subdir2)

# print("All files processed and saved in the output directory.")


# # Move images from hDF_P15_BF_combined to hDF_P15_BF directory
# # 3. 파일 이름명 변경 필요 (1)
# target_directory = "D:\\Cell_location\\23.05.27_hDF_P7_BF"  
# os.makedirs(target_directory, exist_ok=True)
# existing_files = set()  # Set to keep track of existing file names

# for subdir in os.listdir(output_dir1):
#     subdir_path = os.path.join(output_dir1, subdir)
#     if os.path.isdir(subdir_path):
#         for filename in os.listdir(subdir_path):
#             if filename.endswith(".jpg"):
#                 src_path = os.path.join(subdir_path, filename)
#                 dst_path = os.path.join(target_directory, filename)
#                 if filename in existing_files:
#                     # Generate a new unique file name
#                     base_name, extension = os.path.splitext(filename)
#                     counter = 1
#                     while os.path.exists(os.path.join(target_directory , f"{base_name}_{counter}{extension}")):
#                         counter += 1
#                     dst_path = os.path.join(target_directory , f"{base_name}_{counter}{extension}")
#                 existing_files.add(os.path.basename(dst_path))
#                 shutil.move(src_path, dst_path)

# # Move images from hDF_P15_AF_combined to hDF_P15_AF directory
# # 4. 파일 이름명 변경 필요 (1)
# target_directory = "D:\\Cell_location\\23.05.27_hDF_P7_AF"  
# os.makedirs(target_directory, exist_ok=True)
# existing_files = set()  # Set to keep track of existing file names

# for subdir in os.listdir(output_dir2):
#     subdir_path = os.path.join(output_dir2, subdir)
#     if os.path.isdir(subdir_path):
#         for filename in os.listdir(subdir_path):
#             if filename.endswith(".jpg"):
#                 src_path = os.path.join(subdir_path, filename)
#                 dst_path = os.path.join(target_directory, filename)
#                 if filename in existing_files:
#                     # Generate a new unique file name
#                     base_name, extension = os.path.splitext(filename)
#                     counter = 1
#                     while os.path.exists(os.path.join(target_directory , f"{base_name}_{counter}{extension}")):
#                         counter += 1
#                     dst_path = os.path.join(target_directory , f"{base_name}_{counter}{extension}")
#                 existing_files.add(os.path.basename(dst_path))
#                 shutil.move(src_path, dst_path)

# print("Images moved to respective directories.")

# # Delete the hDF_P15_AF_combined directory

# shutil.rmtree(output_dir1)
# shutil.rmtree(output_dir2)

# print("-------------23.05.27_hDF_P7_END.")

# # -------------23.05.26_hDF_P7_START----------------

# # Create output directory
# # 1. 파일명 변경 (2)
# output_dir1 = "D:\\Cell_location\\hDF_P7_BF_combined"
# output_dir2 = "D:\\Cell_location\\hDF_P7_AF_combined"
# os.makedirs(output_dir1, exist_ok=True)
# os.makedirs(output_dir2, exist_ok=True)

# # Use the function
# # 2. 파일 경로 변경 필요 항상 BF먼저 이후 AF. (범위 변경 필요) (6+ 범위)
# for i in range(1, 61): #range(start, stop) 함수에서 stop의 값은 범위에 포함되지 않는다
#     txt_dir1 = rf"D:\deep learning\23.05.26hDF_P7_BFj\labels\{i}.txt"
#     txt_dir2 = rf"D:\deep learning\23.05.26hDF_P7_AFj\labels\{i}.txt"
#     if not os.path.exists(txt_dir1) or not os.path.exists(txt_dir2): continue
#     image_dir1 = rf"D:\YH_23.06.07_backup\23.05.26\hDF_P7_BF\{i}.jpg"
#     image_dir2 = rf"D:\YH_23.06.07_backup\23.05.26\hDF_P7_AF\{i}.jpg"
#     if not os.path.exists(image_dir1) or not os.path.exists(image_dir2): continue
#     output_subdir1 = os.path.join(output_dir1, f"23.05.26_hDF_P7_BF_{i}")
#     output_subdir2 = os.path.join(output_dir2, f"23.05.26_hDF_P7_AF_{i}")
#     compare_txts_and_crop(txt_dir1, txt_dir2, image_dir1, image_dir2, output_subdir1, output_subdir2)

# print("All files processed and saved in the output directory.")


# # Move images from hDF_P15_BF_combined to hDF_P15_BF directory
# # 3. 파일 이름명 변경 필요 (1)
# target_directory = "D:\\Cell_location\\23.05.26_hDF_P7_BF"  
# os.makedirs(target_directory, exist_ok=True)
# existing_files = set()  # Set to keep track of existing file names

# for subdir in os.listdir(output_dir1):
#     subdir_path = os.path.join(output_dir1, subdir)
#     if os.path.isdir(subdir_path):
#         for filename in os.listdir(subdir_path):
#             if filename.endswith(".jpg"):
#                 src_path = os.path.join(subdir_path, filename)
#                 dst_path = os.path.join(target_directory, filename)
#                 if filename in existing_files:
#                     # Generate a new unique file name
#                     base_name, extension = os.path.splitext(filename)
#                     counter = 1
#                     while os.path.exists(os.path.join(target_directory , f"{base_name}_{counter}{extension}")):
#                         counter += 1
#                     dst_path = os.path.join(target_directory , f"{base_name}_{counter}{extension}")
#                 existing_files.add(os.path.basename(dst_path))
#                 shutil.move(src_path, dst_path)

# # Move images from hDF_P15_AF_combined to hDF_P15_AF directory
# # 4. 파일 이름명 변경 필요 (1)
# target_directory = "D:\\Cell_location\\23.05.26_hDF_P7_AF"  
# os.makedirs(target_directory, exist_ok=True)
# existing_files = set()  # Set to keep track of existing file names

# for subdir in os.listdir(output_dir2):
#     subdir_path = os.path.join(output_dir2, subdir)
#     if os.path.isdir(subdir_path):
#         for filename in os.listdir(subdir_path):
#             if filename.endswith(".jpg"):
#                 src_path = os.path.join(subdir_path, filename)
#                 dst_path = os.path.join(target_directory, filename)
#                 if filename in existing_files:
#                     # Generate a new unique file name
#                     base_name, extension = os.path.splitext(filename)
#                     counter = 1
#                     while os.path.exists(os.path.join(target_directory , f"{base_name}_{counter}{extension}")):
#                         counter += 1
#                     dst_path = os.path.join(target_directory , f"{base_name}_{counter}{extension}")
#                 existing_files.add(os.path.basename(dst_path))
#                 shutil.move(src_path, dst_path)

# print("Images moved to respective directories.")

# # Delete the hDF_P15_AF_combined directory

# shutil.rmtree(output_dir1)
# shutil.rmtree(output_dir2)

# print("-------------23.05.26_hDF_P7_END.")
