# NCC: Nanosensor Chemical Cytometry for Aging Heterogeneities in Human Dermal Fibroblasts
This repository contains the code for the paper "Unveiling Aging Heterogeneities in Human Dermal Fibroblasts via Nanosensor Chemical Cytometry".

## Project Overview
Nanosensor Chemical Cytometry (NCC) enables the precise detection of aging-related cellular heterogeneities at the single-cell level. This repository provides the code for training models, detecting cellular features, and extracting relevant data using YOLO-based object detection and additional image processing techniques.

## Project Structure

The project is organized into the following main directories:

1_image_preprocessing/                 # Image brightness normalization and CLAHE  
2_detection/                          # YOLO-based single-cell detection  
3_cell_tracking_feature_extraction/  # Matched cell cropping and feature extraction  
4_passage_prediction/                # Passage number prediction model and scripts  
data/                                # Input image datasets (e.g., p5.zip, p15.zip)

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

## Image Preprocessing
`1_image_preprocessing/intensity_adjustment.py`:  
Applies brightness normalization and CLAHE to standardize input images before detection.


## Matched Cell Cropping & Feature Extraction
This step includes tracking cells across time points and extracting single-cell features for downstream analysis.

- `3_cell_tracking_feature_extraction/crop_matched_0min_10min_cells.py`:
Matches cells between two time points (e.g., 0 min and 10 min) using YOLO-based detection results, then crops the matched regions.

- `3_cell_tracking_feature_extraction/nIR_cell_feature_extraction.py` :
Extracts features such as size, brightness, eccentricity, ROS efflux, and refractive index (computed via an FDTD-based formula) from cropped cell images. The output is saved in Excel format.

## Passage Prediction

Located in `4_passage_prediction/`.

This module predicts the passage number (P5 to P15) of individual cells based on NCC-derived features.

- `4_passage_prediction/passage_prediction_training.py`:  
  Trains a multi-task neural network using features such as ROS efflux, refractive index, and spatial density.
- `4_passage_prediction/predict_passage_probability.py`:  
  Applies the trained model to new single-cell data and outputs prediction probabilities for each passage number.
- `4_passage_prediction/passage_prediction_model.pth`:  
  Pretrained model weights.
- `4_passage_prediction/clustering_params.pkl`:  
  Preprocessing pipeline including StandardScaler, PCA, KMeans, and DBSCAN.

## About the Provided Data and Code

This repository includes a subset of data and code prepared for publication purposes:

- The `data/` folder contains selected example images (10 frames each from P5 and P15 at 0 min and 10 min) used to illustrate the analysis pipeline. Full raw datasets are not included.
- The code has been trimmed to remove personal or environment-specific configurations and includes only the core modules essential for reproducing the analysis flow presented in the paper.

If you require access to the full dataset or the complete analysis code, please contact the corresponding author as indicated in the publication.


## License
This project is licensed under the MIT License. See the LICENSE file for details.
