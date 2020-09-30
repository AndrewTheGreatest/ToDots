import numpy as np 
import copy
import random
from math import e
import statistics
import json
import os.path
from os import path
import argparse

import cv2
from PIL import Image
from matplotlib import cm

"""
list = np.array(list(range(9)) )
print(list[1::3])
"""

blur_amount = 9

beg = cv2.imread("C:\\Users\\Andrew\\Desktop\\Python Stuff\\projects\\calculated Dots\\" + 'look.png')
#beg2 = cv2.imread("C:\\Users\\Andrew\\Desktop\\Python Stuff\\projects\\calculated Dots\\" + 'look2.png')
#print(beg.shape[1])
beg = cv2.GaussianBlur(beg,(blur_amount,blur_amount),0)


flat_img = beg.flatten()
avg_color = (np.average(flat_img[0::3]), np.average(flat_img[1::3]), np.average(flat_img[2::3]))
#avg_color = (255, 255, 255)

beg2 = np.zeros((beg.shape[0],beg.shape[1],beg.shape[2]),np.uint8)
cv2.rectangle(beg2, (0, 0), (beg.shape[1], beg.shape[0]), avg_color, -1)

# compute difference
#difference = cv2.subtract(beg, beg2)
difference = cv2.absdiff(beg, beg2)
Conv_hsv_Gray = cv2.cvtColor(difference, cv2.COLOR_BGR2GRAY)

#print(np.sum(Conv_hsv_Gray.flatten()))

(minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(Conv_hsv_Gray)
b,g,r = (beg[maxLoc[1], maxLoc[0]])
cv2.circle(beg2, maxLoc, 1, (int(b), int(g), int(r)), -1)
cv2.circle(Conv_hsv_Gray, maxLoc, 1, (int(b), int(g), int(r)), -1)


cv2.imshow("beg", beg)
cv2.imshow("blank", beg2)
cv2.imshow("filtered", Conv_hsv_Gray)


cv2.waitKey(0)
cv2.destroyAllWindows()
