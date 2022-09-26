import cv2
import numpy as np

rn = "008"
img_color = cv2.imread(f"test_files/labels{rn}.png",-1)

print(img_color.shape)

unique_numbers = np.unique(img_color)
print(unique_numbers)
print(len(unique_numbers))


temp = img_color.copy()
th = (temp == 1)
temp[th] = 65000

cv2.imwrite(f"test_files/temp_16bits_{rn}.png", temp)