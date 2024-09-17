# NCC
Codes for "Unveiling Aging Heterogeneities in Human Dermal Fibroblasts via Nanosensor Chemical Cytometry".

# Creating yaml file
yaml_content = """
train: /Your_Path_to_Training_Image/
val: /Your_Path_to_Validation_Image/

nc: 1  # Number of classes
names: ['cell']  # Class names
"""

# Write the content to the .yaml file
yaml_file_path = '/Your_Path/hdf.yaml'

with open(yaml_file_path, 'w') as yaml_file:
    yaml_file.write(yaml_content)

print(f"YAML file created at: {yaml_file_path}")

python /Your_Path_to_Train/train.py --img 640 --conf 0.25 --batch 16 --epochs 50 --data /Your_Path/hdf.yaml --weights yolov5s.pt --cache --project /Your_Path_for_Training_Result/ --name model_name


# Training
python /Your_Train_Folder/train.py --img 640 --conf 0.25 --batch 16 --epochs 50 --data /Your_Path/hdf.yaml --weights yolov5s.pt --cache --project /Your_Path_for_Training_Result/ --name model_name

# Detecting
python /Your_Path_to_Detect_File/detect.py --weights /Your_Path_to_Model/model_name.pt --img 640 --conf 0.25 --source /Your_Path_to_Images/ --project /Your_Path_for_Results/ --name Folder_name

## Intensity Adjustment
This code adjusts brightness differences by comparing each image to the average background brightness, then applies CLAHE to enhance contrast, resulting in images with a uniform background.

## Cell Location Comparison
This code allows comparison of the text labels from an original image and later images, crops the regions containing the same objects from both images, and saves them.
Using this code requires images with bounding boxes and corresponding '.txt' files containing coordinate data. The bounding box information from the '.txt' files is used to extract and save the matching object regions from both the before and after images.

## Data Extraction

