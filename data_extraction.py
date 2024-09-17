<<<<<<< HEAD
import cv2
import numpy as np
import math
import os
import pandas as pd
from scipy.interpolate import interp1d

# Set folder paths (for saving images)
bf_save_folder = r"Your_path\example_BF_image"
af_save_folder = r"Your_path\example_AF_image"

# Check if folders exist, if not, create them
if not os.path.exists(bf_save_folder):
    os.makedirs(bf_save_folder)
if not os.path.exists(af_save_folder):
    os.makedirs(af_save_folder)
    
# Set folder path
folder_path = r"Your_path"
# Create a DataFrame to store the results
data = pd.DataFrame(columns=["Filename", "Major Axis", "Minor Axis", "Size(μm²)", "Eccentricity", "FWHM", 
                             "Intensity Mean (First Image)", "Intensity Mean (Second Image)"])

src_dir = r"Your_path_BF"
src2_dir = r"Your_path_AF"
output_filename = "Your_path_to_excel_file/*.xlsx"

# Process all files in the directories
for src_filename in os.listdir(src_dir):
    src_path = os.path.join(src_dir, src_filename)
    
    # Generate the filename in src2 by replacing "_BF_" in src_filename with "_AF_".
    src2_filename = src_filename.replace("_BF_", "_AF_")
    src2_path = os.path.join(src2_dir, src2_filename)

    # Load the images
    src = cv2.imread(src_path, cv2.IMREAD_GRAYSCALE)
    src2 = cv2.imread(src2_path, cv2.IMREAD_GRAYSCALE)
    
    # Adjust the mean value of the images to 80
    src_mean = np.mean(src)
    src_ch = np.clip(src + (80 - src_mean), 0, 255).astype(np.uint8)

    # Make copies of original images for later use
    src_copy = src.copy()
    src2_copy = src2.copy()

    # Image center
    image_center = (src.shape[1] / 2, src.shape[0] / 2)

    # Initialize best values
    best_alpha2 = None
    best_threshold = None
    best_eccentricity = float('inf')
    best_ellipse = None

    # Try alpha2 values from 0 to 5 and threshold values from 80 to 200
    for alpha2 in np.arange(1.0, 5.0, 0.1):
        for threshold in range(80, 128, 1):
            # Adjust contrast
            dst2 = np.clip((1 + alpha2) * src_ch - 128 * alpha2, 0, 255).astype(np.uint8)

            # Threshold
            _, dst2 = cv2.threshold(dst2, threshold, 255, cv2.THRESH_BINARY)

            # Find contours in the image
            contours, _ = cv2.findContours(dst2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            for contour in contours:
                # Minimum enclosing ellipse for each contour
                if contour.shape[0] >= 5:  # as fitEllipse needs at least 5 points
                    ellipse = cv2.fitEllipse(contour)

                    # Ellipse parameters
                    (center, axes, orientation) = ellipse

                    # Calculate the area, eccentricity, major_axis, and minor_axis
                    major_axis = max(axes)
                    minor_axis = min(axes)
                    area = np.pi * (major_axis / 2) * (minor_axis / 2)
                    eccentricity = math.sqrt(1 - (minor_axis / major_axis) ** 2)

                    # Only consider ellipses with a minimum radius of 5
                    if 5 <= minor_axis <= 13 and eccentricity < best_eccentricity:
                        best_eccentricity = eccentricity
                        best_ellipse = ellipse
                        best_alpha2 = alpha2
                        best_threshold = threshold

    # Check if best_alpha2 is None
    if best_alpha2 is None:
        continue

    # Adjust contrast using best alpha2
    dst3 = np.clip((1 + best_alpha2) * src - 128 * best_alpha2, 0, 255).astype(np.uint8)
        
    # Copy the image to draw the circle
    bf_image_with_circle = dst3.copy()
    
    # Ellipse parameters
    (center, axes, orientation) = best_ellipse

    # Increase the size of the ellipse axes by 4 pixels each (2 pixels for each side)
    larger_axes = (axes[0] + 4, axes[1] + 4)

    # Draw the larger ellipse on this copy
    cv2.ellipse(bf_image_with_circle, (center, larger_axes, orientation), (0, 255, 0), 1)

    # Calculate the intensity mean within the ellipse region for the first image
    ellipse_mask = np.zeros_like(src)
    cv2.ellipse(ellipse_mask, best_ellipse, 255, -1)
    intensity_mean = np.mean(src[np.where(ellipse_mask == 255)]) / 255.0

    # Calculate the area, eccentricity, major_axis, and minor_axis
    major_axis = max(axes)
    minor_axis = min(axes)
    area = np.pi * (major_axis / 2) * (minor_axis / 2)
    eccentricity = math.sqrt(1 - (minor_axis / major_axis) ** 2)

    # FWHM  ###FWHM std change
    # Calculate the short diameter passing through the center of the ellipse
    short_diameter = min(axes)
    short_radius = short_diameter / 2
    
    # Get the pixel intensities along the short diameter
    y_values = []
    x_values = list(range(int(center[1] - short_radius), int(center[1] + short_radius)))
    for y in x_values:
        # Check if y is within the valid range
        if y >= 0 and y < src.shape[0]:
            # Calculate the average intensity of the vertical pixels at this location
            intensity_sum = 0
            for x in range(int(center[0] - short_radius), int(center[0] + short_radius)):
                # Check if x is within the valid range
                if x >= 0 and x < src.shape[1]:
                    intensity_sum += src[y, x]
            avg_intensity = intensity_sum / (2 * short_radius)
            # Intensity change
            y_values.append(avg_intensity)
        else:
            y_values.append(0.0)
    
    # Ensure the minimum y values at both ends of the x axis are the same
    min_y_value = min(y_values[0], y_values[-1])
    y_values[0] = min_y_value
    y_values[-1] = min_y_value
    
    # Normalize the y values to the range [0, 1]
    max_y_value = max(y_values)
    min_y_value = min(y_values)
    if max_y_value != min_y_value:
        y_values = [(y - min_y_value) / (max_y_value - min_y_value) for y in y_values]
    else:
        y_values = [0.0] * len(y_values)
    
    # Find the index of the maximum y value
    max_index = y_values.index(max(y_values))
    
    # Split the data into left and right parts
    x_values_left = x_values[:max_index + 1]
    y_values_left = y_values[:max_index + 1]
    x_values_right = x_values[max_index:]
    y_values_right = y_values[max_index:]
    
    # Check if max_y_value and min_y_value are equal
    if max(y_values) != min(y_values):
        # Normalize the y values to the range [0, 1]
        max_y_value = max(y_values)
        min_y_value = min(y_values)
        y_values_left = [(y - min_y_value) / (max_y_value - min_y_value) for y in y_values_left]
        y_values_right = [(y - min_y_value) / (max_y_value - min_y_value) for y in y_values_right]
    else:
        # Set y values to 0.0 if max_y_value and min_y_value are equal
        y_values_left = [0.0] * len(y_values_left)
        y_values_right = [0.0] * len(y_values_right)
    
    # Create interpolation functions for the left and right parts
    f_left = interp1d(y_values_left, x_values_left)
    f_right = interp1d(y_values_right, x_values_right)
    
    # Find the x values where y = 0.5
    try:
        x_05_left = f_left(0.5)
        x_05_right = f_right(0.5)
    except ValueError:
        continue
    
    # Compute the absolute sum of the x values
    if x_05_right is not None and x_05_left is not None:
        fwhm = abs(x_05_right - x_05_left)
    else:
        continue
   
    ## Molecular intensity change
    # Calculate the intensity mean for src_copy
    intensity_mean_src_copy = np.mean(src_copy)

    # Calculate the intensity mean for src2_copy
    intensity_mean_src2_copy = np.mean(src2_copy)

    # Calculate the difference between the means
    difference = intensity_mean_src_copy - intensity_mean_src2_copy

    # Adjust the intensity of src2_copy to match the mean of src_copy
    src2_copy = np.clip(src2_copy + difference, 0, 255).astype(np.uint8)
    
    ######
    # Apply best_alpha2 to the second image and find the ellipse
    dst2_second = np.clip((1 + best_alpha2) * src2 - 128 * best_alpha2, 0, 255).astype(np.uint8)

    # Ellipse parameters
    (center, axes, orientation) = best_ellipse

    # Increase the size of the ellipse axes by 4 pixels each (2 pixels for each side)
    larger_axes = (axes[0] + 4, axes[1] + 4)

    # Copy the image to draw the circle
    af_image_with_circle = dst2_second.copy()

    # Draw the larger ellipse on this copy
    cv2.ellipse(af_image_with_circle, (center, larger_axes, orientation), (0, 255, 0), 1)

    # Draw the larger ellipse on dst2_second
    cv2.ellipse(dst2_second, (center, larger_axes, orientation), (0, 255, 0), 1)

    # Generate the ellipse mask for the second image using the original best_ellipse
    ellipse_mask2 = np.zeros_like(src2_copy)
    cv2.ellipse(ellipse_mask2, best_ellipse, 255, -1)
    intensity_mean2 = np.mean(src2_copy[np.where(ellipse_mask2 == 255)]) / 255.0

    # Write the results to the DataFrame
    data = pd.concat([data, pd.DataFrame({"Filename": [src_filename], "Major Axis": [major_axis * 1.497],
                                          "Minor Axis": [minor_axis * 1.497], "Size(μm²)": [area * 1.497 ** 2],
                                          "Eccentricity": [eccentricity], "FWHM": [fwhm],
                                          "Intensity Mean (First Image)": [intensity_mean],
                                          "Intensity Mean (Second Image)": [intensity_mean2]})],
                     ignore_index=True)

    # Save the image with the circle drawn (BF)
    bf_circle_path = os.path.join(bf_save_folder, src_filename)
    cv2.imwrite(bf_circle_path, bf_image_with_circle)
    
    # Save the image with the circle drawn (AF)
    af_circle_path = os.path.join(af_save_folder, src2_filename)
    cv2.imwrite(af_circle_path, af_image_with_circle)
    
# Save the DataFrame to an Excel file
data.to_excel(os.path.join(folder_path, output_filename))
=======
import cv2
import numpy as np
import math
import os
import pandas as pd
from scipy.interpolate import interp1d

# Set folder paths (for saving images)
bf_save_folder = r"Your_path\example_BF_image"
af_save_folder = r"Your_path\example_AF_image"

# Check if folders exist, if not, create them
if not os.path.exists(bf_save_folder):
    os.makedirs(bf_save_folder)
if not os.path.exists(af_save_folder):
    os.makedirs(af_save_folder)
    
# Set folder path
folder_path = r"Your_path"
# Create a DataFrame to store the results
data = pd.DataFrame(columns=["Filename", "Major Axis", "Minor Axis", "Size(μm²)", "Eccentricity", "FWHM", 
                             "Intensity Mean (First Image)", "Intensity Mean (Second Image)"])

src_dir = r"Your_path_BF"
src2_dir = r"Your_path_AF"
output_filename = "Your_path_to_excel_file/*.xlsx"

# Process all files in the directories
for src_filename in os.listdir(src_dir):
    src_path = os.path.join(src_dir, src_filename)
    
    # Generate the filename in src2 by replacing "_BF_" in src_filename with "_AF_".
    src2_filename = src_filename.replace("_BF_", "_AF_")
    src2_path = os.path.join(src2_dir, src2_filename)

    # Load the images
    src = cv2.imread(src_path, cv2.IMREAD_GRAYSCALE)
    src2 = cv2.imread(src2_path, cv2.IMREAD_GRAYSCALE)
    
    # Adjust the mean value of the images to 80
    src_mean = np.mean(src)
    src_ch = np.clip(src + (80 - src_mean), 0, 255).astype(np.uint8)

    # Make copies of original images for later use
    src_copy = src.copy()
    src2_copy = src2.copy()

    # Image center
    image_center = (src.shape[1] / 2, src.shape[0] / 2)

    # Initialize best values
    best_alpha2 = None
    best_threshold = None
    best_eccentricity = float('inf')
    best_ellipse = None

    # Try alpha2 values from 0 to 5 and threshold values from 80 to 200
    for alpha2 in np.arange(1.0, 5.0, 0.1):
        for threshold in range(80, 128, 1):
            # Adjust contrast
            dst2 = np.clip((1 + alpha2) * src_ch - 128 * alpha2, 0, 255).astype(np.uint8)

            # Threshold
            _, dst2 = cv2.threshold(dst2, threshold, 255, cv2.THRESH_BINARY)

            # Find contours in the image
            contours, _ = cv2.findContours(dst2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            for contour in contours:
                # Minimum enclosing ellipse for each contour
                if contour.shape[0] >= 5:  # as fitEllipse needs at least 5 points
                    ellipse = cv2.fitEllipse(contour)

                    # Ellipse parameters
                    (center, axes, orientation) = ellipse

                    # Calculate the area, eccentricity, major_axis, and minor_axis
                    major_axis = max(axes)
                    minor_axis = min(axes)
                    area = np.pi * (major_axis / 2) * (minor_axis / 2)
                    eccentricity = math.sqrt(1 - (minor_axis / major_axis) ** 2)

                    # Only consider ellipses with a minimum radius of 5
                    if 5 <= minor_axis <= 13 and eccentricity < best_eccentricity:
                        best_eccentricity = eccentricity
                        best_ellipse = ellipse
                        best_alpha2 = alpha2
                        best_threshold = threshold

    # Check if best_alpha2 is None
    if best_alpha2 is None:
        continue

    # Adjust contrast using best alpha2
    dst3 = np.clip((1 + best_alpha2) * src - 128 * best_alpha2, 0, 255).astype(np.uint8)
        
    # Copy the image to draw the circle
    bf_image_with_circle = dst3.copy()
    
    # Ellipse parameters
    (center, axes, orientation) = best_ellipse

    # Increase the size of the ellipse axes by 4 pixels each (2 pixels for each side)
    larger_axes = (axes[0] + 4, axes[1] + 4)

    # Draw the larger ellipse on this copy
    cv2.ellipse(bf_image_with_circle, (center, larger_axes, orientation), (0, 255, 0), 1)

    # Calculate the intensity mean within the ellipse region for the first image
    ellipse_mask = np.zeros_like(src)
    cv2.ellipse(ellipse_mask, best_ellipse, 255, -1)
    intensity_mean = np.mean(src[np.where(ellipse_mask == 255)]) / 255.0

    # Calculate the area, eccentricity, major_axis, and minor_axis
    major_axis = max(axes)
    minor_axis = min(axes)
    area = np.pi * (major_axis / 2) * (minor_axis / 2)
    eccentricity = math.sqrt(1 - (minor_axis / major_axis) ** 2)

    # FWHM  ###FWHM std change
    # Calculate the short diameter passing through the center of the ellipse
    short_diameter = min(axes)
    short_radius = short_diameter / 2
    
    # Get the pixel intensities along the short diameter
    y_values = []
    x_values = list(range(int(center[1] - short_radius), int(center[1] + short_radius)))
    for y in x_values:
        # Check if y is within the valid range
        if y >= 0 and y < src.shape[0]:
            # Calculate the average intensity of the vertical pixels at this location
            intensity_sum = 0
            for x in range(int(center[0] - short_radius), int(center[0] + short_radius)):
                # Check if x is within the valid range
                if x >= 0 and x < src.shape[1]:
                    intensity_sum += src[y, x]
            avg_intensity = intensity_sum / (2 * short_radius)
            # Intensity change
            y_values.append(avg_intensity)
        else:
            y_values.append(0.0)
    
    # Ensure the minimum y values at both ends of the x axis are the same
    min_y_value = min(y_values[0], y_values[-1])
    y_values[0] = min_y_value
    y_values[-1] = min_y_value
    
    # Normalize the y values to the range [0, 1]
    max_y_value = max(y_values)
    min_y_value = min(y_values)
    if max_y_value != min_y_value:
        y_values = [(y - min_y_value) / (max_y_value - min_y_value) for y in y_values]
    else:
        y_values = [0.0] * len(y_values)
    
    # Find the index of the maximum y value
    max_index = y_values.index(max(y_values))
    
    # Split the data into left and right parts
    x_values_left = x_values[:max_index + 1]
    y_values_left = y_values[:max_index + 1]
    x_values_right = x_values[max_index:]
    y_values_right = y_values[max_index:]
    
    # Check if max_y_value and min_y_value are equal
    if max(y_values) != min(y_values):
        # Normalize the y values to the range [0, 1]
        max_y_value = max(y_values)
        min_y_value = min(y_values)
        y_values_left = [(y - min_y_value) / (max_y_value - min_y_value) for y in y_values_left]
        y_values_right = [(y - min_y_value) / (max_y_value - min_y_value) for y in y_values_right]
    else:
        # Set y values to 0.0 if max_y_value and min_y_value are equal
        y_values_left = [0.0] * len(y_values_left)
        y_values_right = [0.0] * len(y_values_right)
    
    # Create interpolation functions for the left and right parts
    f_left = interp1d(y_values_left, x_values_left)
    f_right = interp1d(y_values_right, x_values_right)
    
    # Find the x values where y = 0.5
    try:
        x_05_left = f_left(0.5)
        x_05_right = f_right(0.5)
    except ValueError:
        continue
    
    # Compute the absolute sum of the x values
    if x_05_right is not None and x_05_left is not None:
        fwhm = abs(x_05_right - x_05_left)
    else:
        continue
   
    ## Molecular intensity change
    # Calculate the intensity mean for src_copy
    intensity_mean_src_copy = np.mean(src_copy)

    # Calculate the intensity mean for src2_copy
    intensity_mean_src2_copy = np.mean(src2_copy)

    # Calculate the difference between the means
    difference = intensity_mean_src_copy - intensity_mean_src2_copy

    # Adjust the intensity of src2_copy to match the mean of src_copy
    src2_copy = np.clip(src2_copy + difference, 0, 255).astype(np.uint8)
    
    ######
    # Apply best_alpha2 to the second image and find the ellipse
    dst2_second = np.clip((1 + best_alpha2) * src2 - 128 * best_alpha2, 0, 255).astype(np.uint8)

    # Ellipse parameters
    (center, axes, orientation) = best_ellipse

    # Increase the size of the ellipse axes by 4 pixels each (2 pixels for each side)
    larger_axes = (axes[0] + 4, axes[1] + 4)

    # Copy the image to draw the circle
    af_image_with_circle = dst2_second.copy()

    # Draw the larger ellipse on this copy
    cv2.ellipse(af_image_with_circle, (center, larger_axes, orientation), (0, 255, 0), 1)

    # Draw the larger ellipse on dst2_second
    cv2.ellipse(dst2_second, (center, larger_axes, orientation), (0, 255, 0), 1)

    # Generate the ellipse mask for the second image using the original best_ellipse
    ellipse_mask2 = np.zeros_like(src2_copy)
    cv2.ellipse(ellipse_mask2, best_ellipse, 255, -1)
    intensity_mean2 = np.mean(src2_copy[np.where(ellipse_mask2 == 255)]) / 255.0

    # Write the results to the DataFrame
    data = pd.concat([data, pd.DataFrame({"Filename": [src_filename], "Major Axis": [major_axis * 1.497],
                                          "Minor Axis": [minor_axis * 1.497], "Size(μm²)": [area * 1.497 ** 2],
                                          "Eccentricity": [eccentricity], "FWHM": [fwhm],
                                          "Intensity Mean (First Image)": [intensity_mean],
                                          "Intensity Mean (Second Image)": [intensity_mean2]})],
                     ignore_index=True)

    # Save the image with the circle drawn (BF)
    bf_circle_path = os.path.join(bf_save_folder, src_filename)
    cv2.imwrite(bf_circle_path, bf_image_with_circle)
    
    # Save the image with the circle drawn (AF)
    af_circle_path = os.path.join(af_save_folder, src2_filename)
    cv2.imwrite(af_circle_path, af_image_with_circle)
    
# Save the DataFrame to an Excel file
data.to_excel(os.path.join(folder_path, output_filename))
>>>>>>> 2f0d68de34a35d156d5d2bf7e1e492a828ca0a54
