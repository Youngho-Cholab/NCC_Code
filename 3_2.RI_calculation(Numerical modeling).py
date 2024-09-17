import pandas as pd
import numpy as np

# 읽을 엑셀 파일들의 경로를 지정합니다
file_path = r"C:\ADSC_data\ADSC_D21\ADSC_O21_24.06.25_M.xlsx"
output_paths = r"C:\ADSC_data\ADSC_D21\ADSC_O21_24.06.25_MR.xlsx"


# 엑셀 파일을 읽어서 combined_df에 할당합니다.
combined_df = pd.read_excel(file_path)

###src_image
# # 8번째 열에 0.00204를 곱하고 9열로 나눈 뒤 0.00204를 뺀 값을 10열에 추가
# combined_df['10열'] = (combined_df.iloc[:, 7] * 0.00204 / combined_df.iloc[:, 8]) - 0.00204

# # 10열 값에 0.193을 나누어준 값을 11열에 추가
# combined_df['11열'] = combined_df['10열'] / 0.193

# # 11열 값에 1000을 곱한 값을 12열에 추가
# combined_df['12열'] = combined_df['11열'] * 1000

# #volume of cell
# combined_df['13열'] = 4/3 * np.pi * (combined_df.iloc[:, 2]/2 * combined_df.iloc[:, 3]/2 * (combined_df.iloc[:, 2] + combined_df.iloc[:, 3])/4)

# # attomole·cell⁻¹min⁻¹
# combined_df['14열'] = combined_df['13열'] * 10**-15 * combined_df.iloc[:, 11] * 10**15 / 10

# 15열 값에 굴절률 계산'refractive index (n)'
radius = np.sqrt(combined_df.iloc[:, 4] / np.pi)

# 각각의 변수에 알맞은 값을 할당 x= combined_df['15열']
y = radius
z = combined_df.iloc[:, 6]

combined_df['15열'] = 1.613 + 0.057 * y + 0.503 * np.log(y) + 0.114 * np.log(z) + 0.334 / y + 0.178 / z + 0.012 * (y / z) - 0.015 * (z / y) - 0.673 * np.sqrt(y) - 0.060 * np.sqrt(z)

# # 10열과 11열, 12열의 이름을 변경
# combined_df.rename(columns={'10열': 'H₂O₂_sensor(M)', '11열': 'H₂O₂_cell(M)', '12열': 'H₂O₂_cell(μM)'}, inplace=True)

# # 13열과 14열의 이름을 변경
# combined_df.rename(columns={'13열': 'cell volume(µm³)', '14열': 'femtomole·cell⁻¹min⁻¹'}, inplace=True)

# 15열의 이름을 변경
combined_df.rename(columns={'15열': 'Refractive index [n]'}, inplace=True)

# 결과를 새로운 엑셀 파일로 저장합니다
combined_df.to_excel(output_paths , index=False)
