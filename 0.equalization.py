import cv2
import os
from tqdm import tqdm

input_folder = r"C:\Users\tdg38\Desktop\hDF"
output_folder = r"C:\Users\tdg38\Desktop\hDF_EF"

clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

file_list = os.listdir(input_folder)
for filename in tqdm(file_list, desc='Processing images'):

    img = cv2.imread(os.path.join(input_folder, filename))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    mean_bg = cv2.mean(gray)[0]

    all_mean_bg = sum(cv2.mean(cv2.cvtColor(cv2.imread(os.path.join(input_folder, f)), cv2.COLOR_BGR2GRAY))[0] for f in file_list) / len(file_list)
    alpha = all_mean_bg / mean_bg
    gray = cv2.convertScaleAbs(gray, alpha=alpha, beta=0)

    equalized = clahe.apply(gray)

    cv2.imwrite(os.path.join(output_folder, filename), equalized)
