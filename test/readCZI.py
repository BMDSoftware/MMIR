from aicsimageio import AICSImage
import numpy as np
import cv2

img = AICSImage('POC_HD001_t1_alleAK.czi')
dimentions = img.shape
new_imag = np.zeros((dimentions[3], dimentions[4],4))
ch_1 = img.get_image_data("YXZ", C=0, S=0, T=0)
ch_2 = img.get_image_data("YXZ", C=1, S=0, T=0)
ch_3 = img.get_image_data("YXZ", C=2, S=0, T=0)
ch_4 = img.get_image_data("YXZ", C=3, S=0, T=0)
#print(img.shape)
#print(img.data)
print(img.dims)
print(img.shape)
print(ch_2.shape)
print(type(ch_1))

new_imag[:,:,0] = ch_1[:,:,0]
new_imag[:,:,1] = ch_3[:,:,0]
new_imag[:,:,2] = ch_4[:,:,0]
new_imag[:,:,3] = ch_2[:,:,0]

print(new_imag.shape)


cv2.imwrite(f"test_files/CZI_4_chanels_RGBA.png",new_imag)
cv2.imwrite(f"test_files/CZI_test_ch2.tiff",ch_2)