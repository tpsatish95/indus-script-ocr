import os

import cv2
import matplotlib.pyplot as plt
import numpy as np
import scipy
from PIL import Image, ImageChops
from scipy import ndimage

from helpers.temp import TemporaryFile


def trim(im):

    bg = Image.new(im.mode, im.size, im.getpixel((0, 0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)


def auto_canny(image, sigma=0.33):

    # compute the median of the single channel pixel intensities
    v = np.median(image)

    # apply automatic Canny edge detection using the computed median
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(image, lower, upper)

    return edged


def crop_white(image_path):

    threshold = 250

    while True:
        image_sci = scipy.misc.imread(image_path)

        image_g = ndimage.gaussian_filter(image_sci, 3.0)
        labeled, _ = ndimage.label(image_g > threshold)

        temp_conv = TemporaryFile(".png")

        plt.imsave(temp_conv.name, labeled)
        image_cv = cv2.imread(temp_conv.name)
        temp_conv.cleanup()

        gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (7, 7), 0)
        auto = auto_canny(blurred)

        _, cnts, _ = cv2.findContours(auto.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        screenCnt = sorted(cnts, key=cv2.contourArea, reverse=True)[0]

        x, y, w, h = cv2.boundingRect(screenCnt)
        if w * h > (image_sci.shape[0] * image_sci.shape[1]) * 0.60:
            temp_crop = TemporaryFile(".tif")
            plt.imsave(temp_crop.name, image_sci[y:y + h, x:x + w])

            image_pil = Image.open(temp_crop.name)
            temp_crop.cleanup()
            output = trim(image_pil)
            if output is not None:
                temp_output = TemporaryFile(".tif")
                output.save(temp_output.name)
                return temp_output
        elif threshold == 200:
            image_pil = Image.open(image_path)
            output = trim(image_pil)
            if output is not None:
                temp_output = TemporaryFile(".tif")
                output.save(temp_output.name)
                return temp_output
        else:
            threshold = 200
