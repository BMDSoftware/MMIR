#from algorithmsPlugin import algorithm
from main.algorithmsPlugin import algorithm
#from algorithmsPlugin.plugin_register import *
from main.algorithmsPlugin.plugin_register import *

import numpy as np
import cv2



class ram_fluo_sift(algorithmCore):
    ### Algorithm name, this name must be the same in the register() function
    name = "ram_fluo_sift"
    ## Boolean  that returns whether the registration was successful or not.
    succ = False

    def gray_images(self, im1, im2):
        # convert images to gray scale
        #print(im1.shape)
        #print(im2.shape)

        #img = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY)

        img1 = cv2.rotate(im1, cv2.ROTATE_90_CLOCKWISE)
        img2 = im2[:,:,3]

        return img1, img2

    def feature_extraction(self, img1, img2):
        fExt = cv2.xfeatures2d.SIFT_create()

        gray_negative = abs(255 - img1)
        img1 = gray_negative



        return fExt, img1, img2

    def run(self,request):
        try:
            fixI, movI = self.gray_images(self.fix_image, self.mov_image)

            height, width, _ = self.mov_image.shape

            # get features using SIFT
            fExt, img, img2 = self.feature_extraction(fixI, movI)

            keypoints, descriptors = fExt.detectAndCompute(img, None)
            keypoints2, descriptors2 = fExt.detectAndCompute(img2, None)

            keyDraw1 = cv2.drawKeypoints(img, keypoints, None)
            keyDraw2 = cv2.drawKeypoints(img2, keypoints2, None)

            FLAN_INDEX_KDTREE = 0
            index_params = dict(algorithm=FLAN_INDEX_KDTREE, trees=8)
            search_params = dict(checks=1000)

            flann = cv2.FlannBasedMatcher(index_params, search_params)
            matches = flann.knnMatch(descriptors, descriptors2, k=5)

            good_matches = []

            for m1, m2, *_ in matches:
                # good_matches.append(m1)

                if m1.distance < 0.90 * m2.distance:
                    good_matches.append(m1)

            matches = good_matches
            no_of_matches = len(matches)

            lineMatch = cv2.drawMatches(img, keypoints, img2, keypoints2, matches[:50], None, flags=2)

            p1 = np.zeros((no_of_matches, 2))
            p2 = np.zeros((no_of_matches, 2))

            for i, match in enumerate(matches):
                p1[i, :] = keypoints[match.queryIdx].pt
                p2[i, :] = keypoints2[match.trainIdx].pt

            if no_of_matches > 3:
                homography, mask = cv2.findHomography(p1, p2, cv2.RANSAC)
                transformed_img = cv2.warpPerspective(fixI, homography, (width, height))
                succ = True
                msg =None
            else:
                succ = False
                homography = None
                transformed_img = None
                msg = "less than 4 matches were found, pelase try with another algorithm"

            results = {
                # mandatory
                "succ": succ,
                "warping": transformed_img,
                "homography": homography,
                # optional
                "f_mov": keyDraw1,
                "f_fix": keyDraw2,
                "lineMatch": lineMatch,
                "metrics": None,
                "messages": msg

            }
        except Exception as e:
            msg = str(e)
            results = {
                # mandatory
                "succ": False,
                "warping": None,
                "homography": None,
                # optional
                "f_mov": None,
                "f_fix": None,
                "lineMatch": None,
                "metrics": None,
                "messages": msg

            }


        return results




def initialize() -> None:
    register("ram_fluo_sift", ram_fluo_sift)




