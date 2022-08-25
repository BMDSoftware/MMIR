import SimpleITK as sitk
import numpy as np
import cv2

img2_original  = sitk.ReadImage("output.jpg")
img1 = sitk.ReadImage("../media/img/fixed/arcF.jpg")

img2_original.SetSpacing([1.0,1.0])
img1.SetSpacing([1.0,1.0])


#img2_original = sitk.Cast(img1, sitk.sitkFloat32)

#img1  = sitk.Resample(img1,img2_original)
#sitk.WriteImage(img1, "output_resize.jpg")

image_list = sitk.CheckerBoard(img2_original, img1, [4,4,4])

array = sitk.GetArrayFromImage(image_list)
array_rgb = cv2.cvtColor(array, cv2.COLOR_RGB2BGR)

cv2.imwrite("test_itkto_opencv.jpg",array_rgb)

#sitk.WriteImage(image_list, "chessboard.jpg")
