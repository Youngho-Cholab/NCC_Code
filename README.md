# NCC: Nanosensor Chemical Cytometry for Aging Heterogeneities in Human Dermal Fibroblasts
This repository contains the code for the paper "Unveiling Aging Heterogeneities in Human Dermal Fibroblasts via Nanosensor Chemical Cytometry".

## Project Overview
Nanosensor Chemical Cytometry (NCC) enables the precise detection of aging-related cellular heterogeneities at the single-cell level. This repository provides the code for training models, detecting cellular features, and extracting relevant data using YOLO-based object detection and additional image processing techniques.


## Creating the YAML Configuration
```python
yaml_content = """
train: /Your_Path_to_Training_Image/
val: /Your_Path_to_Validation_Image/

nc: 1  # Number of classes
names: ['cell']  # Class names
"""
```


## Write the content to the .yaml file
```python
yaml_file_path = '/Your_Path/hdf.yaml'

with open(yaml_file_path, 'w') as yaml_file:
    yaml_file.write(yaml_content)

print(f"YAML file created at: {yaml_file_path}")
```

## Training
```sh
python /your_path/train.py --img 640 --conf 0.25 --batch 16 --epochs 50 --data /your_path/hdf.yaml --weights yolov5s.pt --cache --project /your_path/ --name model_name
```

## Detecting
```sh
python /your_path/detect.py --weights /your_path/model_name.pt --img 640 --conf 0.25 --source /your_path_to_images/ --project /your_path/ --name Folder_name
```

## Intensity Adjustment
The intensity adjustment module ensures uniform brightness across images by:

1. Comparing each image's brightness to the average background brightness.
2. Applying Contrast Limited Adaptive Histogram Equalization (CLAHE) to enhance image contrast.

This process helps standardize image backgrounds for better analysis.

## Cell Location Comparison
This code compares the text labels of the original and subsequent images, crops regions containing the same objects from both images, and saves them.
To use this code, images with bounding boxes and corresponding '.txt' files containing coordinate data are required. The bounding box information from the '.txt' files is used to extract and save matching object regions from both the before and after images.

## Data Extraction
This code identifies elliptical boundaries around objects in images and extracts information such as the center, shape, brightness, area, eccentricity, and FWHM, then compares the average intensity between two images. The extracted data is saved to an Excel file.

## Additional Data Extraction
This code imports data from an Excel file and calculates the refractive index using H₂O₂ concentration, cell volume, H₂O₂ efflux rate, and a formula derived from FDTD modeling. The results are saved to a new Excel file.


## License
This project is licensed under the MIT License. See the LICENSE file for details.
