import cv2
import numpy as np


def refineKeypoints(kp, dsk, mask_2):
  good_kp = []  # List of "good keypoint"
  good_dsk = []  # List of "good descriptors"

  # Iterate over all keypoints and descriptors and the good ones to a new list.
  # There is no possibility to mark them unnecessary.
  # https://stackoverflow.com/questions/29180815/delete-matches-in-opencv-keypoints-and-descriptors
  for k, d in zip(kp, dsk):
    x, y = k.pt  # Each keypoint as an x, y tuple  https://stackoverflow.com/questions/35884409/how-to-extract-x-y-coordinates-from-opencv-cv2-keypoint-object

    if mask_2[int(y), int(x)] != 0:
      good_kp.append(k)  # Append keypoint to a list of "good keypoint".
      good_dsk.append(d)  # Append descriptor to a list of "good descriptors".

  return good_kp, good_dsk


#img_color = cv2.imread("../media/img/fixed/bridgF2.PNG")
#img_color2 = cv2.imread("../media/img/moving/bridgeP.jpg")

img_color = cv2.imread("../media/img/fixed/arcF8.jpg")
img_color2 = cv2.imread("../media/img/fixed/arcF.jpg")

#img_color = cv2.imread("../media/img/fixed/chess1.jpg")
#img_color2 = cv2.imread("../media/img/moving/Pat_1.jpg")


# Convert to grayscale.
img = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)
img2 = cv2.cvtColor(img_color2, cv2.COLOR_BGR2GRAY)

height, width, _ = img_color2.shape

#img = cv2.resize(img, (width, height), interpolation = cv2.INTER_AREA)

#_,img2 = cv2.threshold(img2,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
#_,img = cv2.threshold(img,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)




#feature extractor

fExt = cv2.xfeatures2d.SIFT_create()
#fExt =  cv2.xfeatures2d.BriefDescriptorExtractor_create()
#fExt = cv2.AKAZE_create()
#fExt = cv2.ORB_create(nfeatures=100)

#rows, cols = height, width
#mask = np.full((rows, cols), 255, np.uint8) # cv2.imread(some_mask_file)
#mask_2 = mask.copy()  #cv2.imread(some_additional_mask_file)
#mask_2[:, 0:cols//2] = 0


keypoints, descriptors = fExt.detectAndCompute(img, None)
keypoints2, descriptors2 = fExt.detectAndCompute(img2, None)


#keyDraw1 = cv2.drawKeypoints(img, keypoints, None)
#keyDraw1 = cv2.drawKeypoints(img, keypoints, None, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
#keyDraw2 = cv2.drawKeypoints(img2, keypoints2, None)
#keyDraw2 = cv2.drawKeypoints(img2, keypoints2, None,  flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

#cv2.imwrite("Image_before.jpg", keyDraw1)
#cv2.imwrite("Image2_before.jpg", keyDraw2)


#keypoints, descriptors = refineKeypoints(keypoints, descriptors, mask_2)
#keypoints2, descriptors2 = refineKeypoints(keypoints2, descriptors2,mask_2)



keyDraw1 = cv2.drawKeypoints(img, keypoints, None)
#keyDraw1 = cv2.drawKeypoints(img, keypoints, None, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
keyDraw2 = cv2.drawKeypoints(img2, keypoints2, None)
#keyDraw2 = cv2.drawKeypoints(img2, keypoints2, None,  flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

cv2.imwrite("Image.jpg", keyDraw1)
cv2.imwrite("Image2.jpg", keyDraw2)

#feature matching
# We create a Brute Force matcher with
# Hamming distance as measurement mode.

FLAN_INDEX_KDTREE = 0
index_params = dict (algorithm = FLAN_INDEX_KDTREE, trees=8)
search_params = dict (checks=1000)

#bf = cv2.BFMatcher()
#bf = cv2.BFMatcher(cv2.NORM_L1, crossCheck=True)
#bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

flann = cv2.FlannBasedMatcher(index_params, search_params)
matches = flann.knnMatch (descriptors, descriptors2,k=5)

#matcher = cv2.DescriptorMatcher_create(cv2.DescriptorMatcher_BRUTEFORCE_HAMMING)
#matches = matcher.knnMatch (descriptors, descriptors2, 2)

good_matches = []

for m1, m2, *_  in matches:
  #good_matches.append(m1)

  if m1.distance < 0.90*m2.distance:
    good_matches.append(m1)

matches = good_matches
#matches = good_matches[:2] + good_matches[3:]
#matches = bf.knnMatch(descriptors,descriptors2, k= 2)
# Sort matches on the basis of their Hamming distance.
#matches = sorted(matches, key = lambda x:x.distance)

# Take the top 90 % matches forward.
#matches = matches[:int(len(matches)*0.9)]
no_of_matches = len(matches)

print(matches[:20])
print(no_of_matches)


lineMatch = cv2.drawMatches(img, keypoints, img2, keypoints2, matches[:50], None, flags=2)
#lineMatch = cv2.drawMatchesKnn(img, keypoints, img2, keypoints2, matches[:20], None, flags=2)
cv2.imwrite("lineMatch.jpg", lineMatch)

# Define empty matrices of shape no_of_matches * 2.
p1 = np.zeros((no_of_matches, 2))
p2 = np.zeros((no_of_matches, 2))

for i, match in enumerate(matches):
  print("#"*50)
  print(match)
  print(match.queryIdx)
  print(match.trainIdx)
  print(keypoints[match.queryIdx])
  print(keypoints2[match.trainIdx])
  print(keypoints[match.queryIdx].pt)
  print(keypoints2[match.trainIdx].pt)
  print("#" * 50)
  p1[i, :] = keypoints[match.queryIdx].pt
  p2[i, :] = keypoints2[match.trainIdx].pt


# Find the homography matrix.
print(p1, p2)
print(matches)

imcol= img_color.copy()
imcol2= img_color2.copy()
for p in p1:
  p = tuple(int(item) for item in p)

  ImageP1 = cv2.circle(imcol, p, radius=5, color=(0, 0, 255), thickness=-1)
for p in p2:
  p = tuple(int(item) for item in p)
  ImageP2 = cv2.circle(imcol2, p, radius=5, color=(0, 255, 0), thickness=-1)

cv2.imwrite('ImageP1.jpg', ImageP1)
cv2.imwrite('ImageP2.jpg', ImageP2)

homography, mask = cv2.findHomography( p1,p2,cv2.RANSAC )


# Use this matrix to transform the
# colored image wrt the reference image.


print(height, width)
print(img.shape)
print(homography)

transformed_img = cv2.warpPerspective(img_color, homography, (width, height))

#cv2.imshow("Image", img)


cv2.imwrite('output.jpg', transformed_img)



