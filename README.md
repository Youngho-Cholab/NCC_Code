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
This code compares the text labels of the original and subsequent images, crops regions containing the same objects from both images, and saves them.
To use this code, images with bounding boxes and corresponding '.txt' files containing coordinate data are required. The bounding box information from the '.txt' files is used to extract and save matching object regions from both the before and after images.

## Data Extraction
This code identifies elliptical boundaries around objects in images and extracts information such as the center, shape, brightness, area, eccentricity, and FWHM, then compares the average intensity between two images. The extracted data is saved to an Excel file.

## Additional Data Extraction
This code imports data from an Excel file and calculates the refractive index using H₂O₂ concentration, cell volume, H₂O₂ efflux rate, and a formula derived from FDTD modeling. The results are saved to a new Excel file.
