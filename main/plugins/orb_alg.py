#from algorithmsPlugin import algorithm
from main.algorithmsPlugin import algorithm
#from algorithmsPlugin.plugin_register import *
from main.algorithmsPlugin.plugin_register import *

import numpy as np
import cv2




class orb_alg(algorithmCore):
    name = "Orb"

    ## Boolean  that returns whether the registration was successful or not.
    succ = False

    def feature_extraction(self, img1, img2):
        fExt = cv2.ORB_create(nfeatures=1000)
        return fExt, img1, img2

    def run(self,request):
        try:
            # convert images to gray scale
            img = cv2.cvtColor(self.fix_image, cv2.COLOR_BGR2GRAY)
            img2 = cv2.cvtColor(self.mov_image, cv2.COLOR_BGR2GRAY)

            height, width, *_ = self.mov_image.shape

            # get features using orb
            fExt, img, img2 = self.feature_extraction(img, img2)

            keypoints, descriptors = fExt.detectAndCompute(img, None)
            keypoints2, descriptors2 = fExt.detectAndCompute(img2, None)

            keyDraw1 = cv2.drawKeypoints(img, keypoints, None)
            keyDraw2 = cv2.drawKeypoints(img2, keypoints2, None)

            matcher = cv2.BFMatcher()
            matches = matcher.match(descriptors, descriptors2)

            #good_matches = []

            #for m1, m2, *_ in matches:
                # good_matches.append(m1)

             #   if m1.distance < 0.65 * m2.distance:
              #      good_matches.append(m1)

            #matches = good_matches

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
                ## Fix values as metrics just used as example
                "metrics": {"metrica1":5, "metrica2": "good", "metric3": 0.05},
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
    register("Orb", orb_alg)


