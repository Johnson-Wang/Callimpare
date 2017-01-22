__author__ = 'xwangan'
import os
import re
import cv2 as cv
from skimage.filter import roberts, sobel

def edge_detection(imag_mat, method="sobel"):
    if method == "sobel":
        img_double = sobel(imag_mat)
        return cv.convertScaleAbs(img_double, alpha = 255. / img_double.max())
    elif method == "canny":
        return cv.Canny(imag_mat, 100, 200)
