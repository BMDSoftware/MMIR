#from algorithms import algorithm
from main.algorithms import algorithm
#from algorithms.plugin_register import *
from main.algorithms.plugin_register import *

import numpy as np
import cv2



class sift_algorithm(algorithmCore):
    ### Algorithm name, this name must be the same in the register() function
    name = "Sift"
    ## Boolean  that returns whether the registration was successful or not.
    succ = False

    def run(self):

        #convert images to gray scale
        img = cv2.cvtColor(self.fix_image, cv2.COLOR_BGR2GRAY)
        img2 = cv2.cvtColor(self.mov_image, cv2.COLOR_BGR2GRAY)


        height, width, _ = self.mov_image.shape

        #get features using SIFT
        fExt = cv2.xfeatures2d.SIFT_create()

        keypoints, descriptors = fExt.detectAndCompute(img, None)
        keypoints2, descriptors2 = fExt.detectAndCompute(img2, None)

        keyDraw1 = cv2.drawKeypoints(img, keypoints, None)
        keyDraw2 = cv2.drawKeypoints(img2, keypoints2, None)

        FLAN_INDEX_KDTREE = 0
        index_params = dict(algorithm=FLAN_INDEX_KDTREE, trees=8)
        search_params = dict(checks=1000)

        flann = cv2.DescriptorMatcher_create(cv2.DescriptorMatcher_FLANNBASED)
        matches = flann.knnMatch(descriptors, descriptors2, k=8)

        good_matches = []

        for m1, m2, *_ in matches:
            # good_matches.append(m1)

            if m1.distance < 0.65 * m2.distance:
                good_matches.append(m1)

        matches = good_matches

        lineMatch = cv2.drawMatches(self.fix_image, keypoints, self.mov_image, keypoints2, matches[:50], None, flags=2)

        no_of_matches = len(matches)

        # Define empty matrices of shape no_of_matches * 2.
        p1 = np.zeros((no_of_matches, 2))
        p2 = np.zeros((no_of_matches, 2))

        for i, match in enumerate(matches):
            p1[i, :] = keypoints[match.queryIdx].pt
            p2[i, :] = keypoints2[match.trainIdx].pt

        if no_of_matches > 3:
            homography, mask = cv2.findHomography(p1, p2, cv2.RANSAC)
            transformed_img = cv2.warpPerspective(self.fix_image, homography, (width, height))
            succ = True
        else:
            succ = False
            homography = None


        results = {
            #mandatory
            "succ" : succ,
            "warping": transformed_img,
            "homography": homography,
            #optional
            "f_mov":keyDraw1,
            "f_fix": keyDraw2,
            "lineMatch" : lineMatch,

        }

        return results


def initialize() -> None:
    register("Sift", sift_algorithm)




