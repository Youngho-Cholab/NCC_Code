<<<<<<< HEAD
import pandas as pd
import numpy as np

# Read the Excel file and specify the paths
file_path = r"Your_path_to_excel_file/*.xlsx"
output_path = r"Your_path_to_excel_file/*.xlsx"

# Load the Excel file into a DataFrame
combined_df = pd.read_excel(file_path)

### H₂O₂ related calculations ###

# Multiply the values in column 8 by 0.00204, divide by column 9, subtract 0.00204, and add the result to column 10
combined_df['Column 10'] = (combined_df.iloc[:, 7] * 0.00204 / combined_df.iloc[:, 8]) - 0.00204

# Divide the values in column 10 by 0.193 and add the result to column 11
combined_df['Column 11'] = combined_df['Column 10'] / 0.193

# Multiply the values in column 11 by 1000 and add the result to column 12
combined_df['Column 12'] = combined_df['Column 11'] * 1000

### Cell volume calculation ###
combined_df['Cell volume (µm³)'] = 4/3 * np.pi * (combined_df.iloc[:, 2]/2 * combined_df.iloc[:, 3]/2 * (combined_df.iloc[:, 2] + combined_df.iloc[:, 3])/4)

### attomole·cell⁻¹min⁻¹ calculation ###
combined_df['H₂O₂ efflux rate (femtomole·cell⁻¹min⁻¹)'] = combined_df['Cell volume (µm³)'] * 10**-15 * combined_df.iloc[:, 11] * 10**15 / 10

### Refractive Index calculation ###

# Calculate the radius
radius = np.sqrt(combined_df.iloc[:, 4] / np.pi)

# Use column 6 for z variable
z = combined_df.iloc[:, 6]

# Add the refractive index calculation to column 15
combined_df['Refractive index [n]'] = 1.613 + 0.057 * radius + 0.503 * np.log(radius) + 0.114 * np.log(z) + 0.334 / radius + 0.178 / z + 0.012 * (radius / z) - 0.015 * (z / radius) - 0.673 * np.sqrt(radius) - 0.060 * np.sqrt(z)

### Rename the columns ###
combined_df.rename(columns={
    'Column 10': 'H₂O₂_sensor (M)',
    'Column 11': 'H₂O₂_cell (M)',
    'Column 12': 'H₂O₂_cell (μM)',
    'Cell volume (µm³)': 'Cell volume (µm³)',
    'H₂O₂ efflux rate (femtomole·cell⁻¹min⁻¹)': 'H₂O₂ efflux rate (femtomole·cell⁻¹min⁻¹)',
    'Refractive index [n]': 'Refractive index [n]'
}, inplace=True)

# Save the results to a new Excel file
combined_df.to_excel(output_path, index=False)
=======
import pandas as pd
import numpy as np

# Read the Excel file and specify the paths
file_path = r"Your_path_to_excel_file/*.xlsx"
output_path = r"Your_path_to_excel_file/*.xlsx"

# Load the Excel file into a DataFrame
combined_df = pd.read_excel(file_path)

### H₂O₂ related calculations ###

# Multiply the values in column 8 by 0.00204, divide by column 9, subtract 0.00204, and add the result to column 10
combined_df['Column 10'] = (combined_df.iloc[:, 7] * 0.00204 / combined_df.iloc[:, 8]) - 0.00204

# Divide the values in column 10 by 0.193 and add the result to column 11
combined_df['Column 11'] = combined_df['Column 10'] / 0.193

# Multiply the values in column 11 by 1000 and add the result to column 12
combined_df['Column 12'] = combined_df['Column 11'] * 1000

### Cell volume calculation ###
combined_df['Cell volume (µm³)'] = 4/3 * np.pi * (combined_df.iloc[:, 2]/2 * combined_df.iloc[:, 3]/2 * (combined_df.iloc[:, 2] + combined_df.iloc[:, 3])/4)

### attomole·cell⁻¹min⁻¹ calculation ###
combined_df['H₂O₂ efflux rate (femtomole·cell⁻¹min⁻¹)'] = combined_df['Cell volume (µm³)'] * 10**-15 * combined_df.iloc[:, 11] * 10**15 / 10

### Refractive Index calculation ###

# Calculate the radius
radius = np.sqrt(combined_df.iloc[:, 4] / np.pi)

# Use column 6 for z variable
z = combined_df.iloc[:, 6]

# Add the refractive index calculation to column 15
combined_df['Refractive index [n]'] = 1.613 + 0.057 * radius + 0.503 * np.log(radius) + 0.114 * np.log(z) + 0.334 / radius + 0.178 / z + 0.012 * (radius / z) - 0.015 * (z / radius) - 0.673 * np.sqrt(radius) - 0.060 * np.sqrt(z)

### Rename the columns ###
combined_df.rename(columns={
    'Column 10': 'H₂O₂_sensor (M)',
    'Column 11': 'H₂O₂_cell (M)',
    'Column 12': 'H₂O₂_cell (μM)',
    'Cell volume (µm³)': 'Cell volume (µm³)',
    'H₂O₂ efflux rate (femtomole·cell⁻¹min⁻¹)': 'H₂O₂ efflux rate (femtomole·cell⁻¹min⁻¹)',
    'Refractive index [n]': 'Refractive index [n]'
}, inplace=True)

# Save the results to a new Excel file
combined_df.to_excel(output_path, index=False)
>>>>>>> 2f0d68de34a35d156d5d2bf7e1e492a828ca0a54
