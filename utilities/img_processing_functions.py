# -*- coding: utf-8 -*-
"""
Created on Thu Oct 27 13:39:07 2022

@author: moallemi
"""


import numpy as np
import cv2
import glob
from pathlib import Path
from matplotlib import pyplot as plt

#functions

# def apply_sharpen_filt(image):
    
#     sharpen_filter = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
#     sharped_img = cv2.filter2D(image, -1, sharpen_filter)
    
#     return sharped_img


def unsharp_mask(image, kernel_size=(5, 5), sigma=1.0, amount=1.0, threshold=0):
    """Return a sharpened version of the image, using an unsharp mask."""
    blurred = cv2.GaussianBlur(image, kernel_size, sigma)
    sharpened = float(amount + 1) * image - float(amount) * blurred
    sharpened = np.maximum(sharpened, np.zeros(sharpened.shape))
    sharpened = np.minimum(sharpened, 255 * np.ones(sharpened.shape))
    sharpened = sharpened.round().astype(np.uint8)
    if threshold > 0:
        low_contrast_mask = np.absolute(image - blurred) < threshold
        np.copyto(sharpened, image, where=low_contrast_mask)
    return sharpened