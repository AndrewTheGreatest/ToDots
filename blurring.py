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

blur_amount = 157
diff_blur_amount = 157

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
difference = cv2.GaussianBlur(difference,(diff_blur_amount,diff_blur_amount),0)


cv2.imshow("beg", beg)
cv2.imshow("blank", beg2)
cv2.imshow("filtered", difference)


cv2.waitKey(0)
cv2.destroyAllWindows()
