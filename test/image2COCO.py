import numpy as np
from skimage.measure import label, regionprops, find_contours, approximate_polygon
from matplotlib import pyplot as plt
import cv2
import json

def close_contour(contour):
    if not np.array_equal(contour[0], contour[-1]):
        contour = np.vstack((contour, contour[0]))
    return contour


class MyImage:
    def __init__(self, path):
        self.img = cv2.imread(path,-1)
        self.split = path.split("/")
        self.__name = self.split[-1]

    def __str__(self):
        return self.__name

def seg2coco(image, classes, dict, id_image ):
    # annotation id
    idAnn = 0


    for cindx, c in enumerate(classes):


        channel = image[:,:,cindx]
        ##count every element of each class
        #instances = [ x for x in np.unique(channel) if x != 0 ]
        #print(instances)
        #print("instances: ", len(instances))

        #if(len(instances)>1):
         #
        #else:
        #labeled_img = channel
        labeled_img = label(channel)

        regions = regionprops(labeled_img)
        print("channel: ", cindx)
        print("regions: ",len(regions))

        #fig, ax = plt.subplots()
        #ax.imshow( channel.astype(np.uint8), cmap=plt.cm.gray)

        # pad mask to close contours of shapes which start and end at an edge
        padded_binary_mask = np.pad(labeled_img, pad_width=1, mode='constant', constant_values=0)
        contours = find_contours(padded_binary_mask, 0.5)
        contours = np.subtract(contours, 1)
        print("contours: ", len(contours))

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
            #ax.axis('image')
            #ax.set_xticks([])
            #ax.set_yticks([])
            #plt.savefig(f'contour_{cindx}_.png')

                #_, mask = cv2.threshold( np.asarray(labeled_img, dtype="uint8") , 127, 1, cv2.THRESH_BINARY )
                #temp = (mask == 0)
                #mask[temp] = False
                #temp = (mask == 1)
                #mask[temp] = True
                #print(mask)
                #print(type(mask))
                #print(np.max(mask))

                #cv2.imwrite(f"maskv1_{cindx}.png", mask )
                #mask2 = np.array(mask, dtype=bool)
                #mask.astype(dtype=bool)

                #print(mask2)

                #print(type(mask2))
                #print(np.max(mask2))
                #cv2.imwrite(f"mask_{cindx}.png", np.asarray(mask2, dtype="uint8")*255)

                #contours = find_contours(labeled_img, level = 0.8)
                #contours, hierarchy = cv2.findContours(np.asarray(labeled_img, dtype="uint8"), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
                #contours2 = find_contours(labeled_img, 0.5)

                #print("contours: ", len(contours))
                #print("contours2: ", len(contours2))

                #print("contours: ", contours)
                #print("contours2: ", contours2)


                #image_copy= np.zeros((channel.shape[0], channel.shape[1], 3))
                #image_copy[:,:,0] = channel.astype(np.uint8)
                #image_copy[:,:,1] = channel.astype(np.uint8)
                #image_copy[:,:,2] = channel.astype(np.uint8)
                #cv2.imwrite(f"before_contours_{cindx}.png", image_copy)

                #cv2.drawContours(image_copy, contours, -1, (np.random.randint(255),np.random.randint(255),np.random.randint(255)), 20)


                #for contour in contours:
                #    print("contour: ",contour)

                #for contour2 in contours2:

                 #   contour2 = close_contour(contour2)
                  #  contour2 = approximate_polygon(contour2, 0)
                   # contour2 = np.flip(contour2, axis=1)
                   # segmentation = contour.ravel().tolist()

                    #print ("contour2: ", segmentation)
                #    cv2.drawContours(image_copy, contour, -1,
                #                     (np.random.randint(255), np.random.randint(255), np.random.randint(255)), 5)
                #cv2.imwrite(f"mask_{cindx}.png", image_copy)
            #        contour = np.flip(contour, axis=1)
            #        #segmentation = contour.ravel().tolist()
            #        ax.plot(contour[:, 0], contour[:, 1], linewidth=2)
            #        # print("area: ",area, " contour_x ",contour[:, 1])
            #        #print(segmentation)
            #        #y, x = contour
            #        #print(len(y), len(x) )
            #
            # ax.axis('image')
            # ax.set_xticks([])
            # ax.set_yticks([])
            # plt.savefig(f'contour_{cindx}_.png')

            # for i in instances:
            #     print(i)


    return dict


def main():


    references_numbers = ['008', '017', '020', '021', '028']
    #references_numbers = ['017']
    for rn in references_numbers:
        #rn="008"
        #id_image
        # this implementation create a file per image with a batch processing all the images must be in only one json
        indf = 1

        img = MyImage(f"test_files/join_{rn}_16bits.png")
        print("image: ", img)

        #scaled_f_down = cv2.resize(img.img, None, fx=0.2, fy=0.2, interpolation=cv2.INTER_LINEAR)
        height,width,depth = img.img.shape
        #height,width,depth = scaled_f_down.shape
        coco = {}
        coco["images"] = []
        coco["annotations"] = []
        coco["categories"] = []

        classes = [ "Crypts","Mucosa","BG"]
        ##create categories
        for cindx, c in enumerate(classes):
            coco["categories"].append({"id": cindx + 1, "name": c})


        if depth == len(classes):
            ##create images
            coco["images"].append({"file_name": str(img), "height": height, "width": width, "id": indf})
            new_dict = seg2coco(img.img, classes, coco, indf)
            #new_dict = seg2coco(scaled_f_down, classes, coco, indf)
            json_string = json.dumps(new_dict)
            with open(f'test_files/json_coco_{rn}_{indf}.json', 'w') as outfile:
                outfile.write(json_string)
            #print(new_dict)
        else:
            print("each channel is a class, please verify that its number of classes is the same as the depth of the image")



if __name__ == '__main__':
    main()