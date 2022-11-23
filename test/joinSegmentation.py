import cv2
import numpy as np
from skimage.measure import label, regionprops, find_contours, approximate_polygon
from matplotlib import pyplot as plt


references_numbers = ['008','017','020','021','028']

def close_contour(contour):
    if not np.array_equal(contour[0], contour[-1]):
        contour = np.vstack((contour, contour[0]))
    return contour

for rn in references_numbers:
    ### Read images ###
    #print(rn)
    img_bg = cv2.imread(f"../../test images/Segmented/background/ID_0{rn}01_MaskBackground.png")
    #print(img_bg.shape)
    img_Mucosa = cv2.imread(f"../../test images/Segmented/Mucosa/ID_{rn}_mask_opening2.png")
    #print(img_Mucosa.shape)
    img_crypt = cv2.imread(f"../../test images/Segmented/crypt/ID_0{rn}01_MosaicityCorrected_MM_mask_mask_opening.png")
    #print(img_crypt.shape)

    ### find the instances ###

    #negative = abs(255 - img_crypt[:,:,0])

    kernel = np.ones((8, 8), np.uint8)


    img_erosion = cv2.erode(img_crypt, kernel, iterations=1)
    img_crypt = cv2.dilate(img_erosion, kernel, iterations=1)

    #label_Cr = label(img_crypt[:,:,0])
    label_Cr = label(img_crypt[:,:,0])
    #regionsCr = regionprops(label_Cr)



    #unique_numbers = np.unique(label_Cr)
    #print(unique_numbers)
    #print(len(unique_numbers))
    #print(len(regionsCr))


    #cv2.imwrite(f"test_files/labels_8bits{rn}.png", label_Cr)


    #cv2.imwrite(f"test_files/labels{rn}.png", label_Cr_16)


    # fig, ax = plt.subplots()
    # ax.imshow(img_crypt, cmap=plt.cm.gray)
    #
    # for propsCr in regionsCr:
    #     label_p = propsCr.label
    #     contours = find_contours(label_Cr == label_p,0.5 )
    #     for contour in contours:
    #         contour = close_contour(contour)
    #         contour = np.flip(contour, axis=1)
    #         #segmentation = contour.ravel().tolist()
    #         ax.plot(contour[:, 0], contour[:, 1], linewidth=2)
    #         # print("area: ",area, " contour_x ",contour[:, 1])
    #         #print(segmentation)
    #
    #         #y, x = contour
    #         #print(len(y), len(x) )
    #
    # ax.axis('image')
    # ax.set_xticks([])
    # ax.set_yticks([])
    # plt.savefig('foo.png')

    joinimage = img_bg


    joinimage[:,:,0] =  img_bg[:,:,0]
    joinimage[:,:,1] =  img_Mucosa[:,:,1]
    joinimage[:,:,2] =  img_crypt[:,:,0]


    cv2.imwrite(f"test_files/mucosa_8bits_{rn}.png", img_Mucosa[:,:,1])
    cv2.imwrite(f"test_files/bg_8bits_{rn}.png", img_bg[:,:,0])
    cv2.imwrite(f"test_files/crypt_8bits_{rn}.png", img_crypt[:,:,0])
    joinimage = cv2.cvtColor(joinimage, cv2.COLOR_BGR2RGB)
    cv2.imwrite(f"test_files/join_{rn}_8bits_.png", joinimage)

    #label_Cr_16 = label_Cr.astype(np.uint16)
    label_Cr_16 = (img_crypt[:,:,1].astype(np.uint16))*257
    mucosa_16 = (img_Mucosa[:,:,1].astype(np.uint16))*257
    bg_16 = (img_bg[:,:,0].astype(np.uint16))*257

    joinimage_16 = img_bg.astype(np.uint16)

    joinimage_16[:, :, 0] = bg_16
    joinimage_16[:, :, 1] = mucosa_16
    joinimage_16[:, :, 2] = label_Cr_16

    print("#"*60)
    print(np.max(label_Cr_16))
    print(np.max(mucosa_16))
    print(np.max(bg_16))
    print(np.max(joinimage_16))
    print("#" * 60)

    cv2.imwrite(f"test_files/mucosa_16bits_{rn}.png", mucosa_16)
    cv2.imwrite(f"test_files/bg_16bits_{rn}.png", bg_16)
    cv2.imwrite(f"test_files/crypt_16bits_{rn}.png", label_Cr_16)
    joinimage_16 = cv2.cvtColor(joinimage_16, cv2.COLOR_BGR2RGB)
    cv2.imwrite(f"test_files/join_{rn}_16bits.png", joinimage_16)

    np.savez(f"test_files/join_{rn}_16bits.npz", joinimage_16 )









