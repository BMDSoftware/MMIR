import numpy as np
from skimage.measure import label, regionprops, find_contours, approximate_polygon
from matplotlib import pyplot as plt
import json


def close_contour(contour):
    if not np.array_equal(contour[0], contour[-1]):
        contour = np.vstack((contour, contour[0]))
    return contour



def seg2coco(image, classes, dict, id_image ):
    # annotation id
    idAnn = 0

    for cindx, c in enumerate(classes):


        channel = image[:,:,cindx]
        ##count every element of each class
        instances = [ x for x in np.unique(channel) if x != 0 ]
        #print(instances)
        print("instances: ", len(instances))

        #if(len(instances)>1):
        #    labeled_img = label(channel)
        #else:
        #    labeled_img = channel

        labeled_img = label(channel)
        regions = regionprops(labeled_img)
        print("regions: ",len(regions))

        #fig, ax = plt.subplots()
        #ax.imshow( channel.astype(np.uint8), cmap=plt.cm.gray)

        # pad mask to close contours of shapes which start and end at an edge
        padded_binary_mask = np.pad(labeled_img, pad_width=1, mode='constant', constant_values=0)
        contours = find_contours(padded_binary_mask, 0.5)
        contours = np.subtract(contours, 1)

        for contIndx, props in enumerate(regions) :
            area = props.area
            bbox = props.bbox
            #label_p = props.label
            #if (len(instances) > 1):



            contour = contours[contIndx]
            #for contour in contours:
            contour = close_contour(contour)
            contour = approximate_polygon(contour, 0)
            if len(contour) < 3:
                continue
            contour = np.flip(contour, axis=1)
            #ax.plot(contour[:, 0], contour[:, 1], linewidth=2)


            segmentation = contour.ravel().tolist()
            # after padding and subtracting 1 we may get -0.5 points in our segmentation
            segmentation = [0 if i < 0 else i for i in segmentation]
            dict["annotations"].append(
                {
                    "id": idAnn,
                    "segmentation": [segmentation],
                    "area": float(area),
                    "bbox": [bbox[1], bbox[0], bbox[3] - bbox[1], bbox[2] - bbox[0]],
                    "iscrowd": 0,
                    "image_id": id_image,
                    "category_id": cindx+1,

                }
            )
            idAnn = idAnn + 1

    return dict

