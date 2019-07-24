"""Attempt at edge detection. Doesn't work so well."""
from typing import Tuple, Iterable

import cv2
import numpy
from numpy import ndarray

from ai_track.core.position import Position
from ai_track.position_detection import watershedding, iso_intensity_curvature
from ai_track.position_detection.iso_intensity_curvature import ImageDerivatives




def background_removal(orignal_image_8bit: ndarray, threshold: ndarray):
    """A simple background removal using two algoritms"""

    # Remove everything below 10%
    absolute_thresh = int(0.01 * 255)
    threshold[orignal_image_8bit < absolute_thresh] = 0

    # Remove using Triangle method
    blur = numpy.empty_like(orignal_image_8bit[0])
    otsu_thresh = numpy.empty_like(orignal_image_8bit[0])
    for z in range(orignal_image_8bit.shape[0]):
        cv2.GaussianBlur(orignal_image_8bit[z], (5, 5), 0, dst=blur)
        cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_TRIANGLE, dst=otsu_thresh)
        threshold[z] &= otsu_thresh


def adaptive_threshold(image_8bit: ndarray, out: ndarray, block_size: int):
    """A simple, adaptive threshold. Intensities below 10% are removed, as well as intensities that fall below an
    adaptive Gaussian threshold.
    """
    for z in range(image_8bit.shape[0]):
        cv2.adaptiveThreshold(image_8bit[z], 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_size,
                              2, dst=out[z])
    background_removal(image_8bit, out)


def advanced_threshold(image_8bit: ndarray, out: ndarray, block_size: int):
    adaptive_threshold(image_8bit, out, block_size)

    curvature_out = numpy.full_like(image_8bit, 255, dtype=numpy.uint8)
    iso_intensity_curvature.get_negative_gaussian_curvatures(image_8bit, ImageDerivatives(), curvature_out)
    out &= curvature_out

    fill_threshold(out)
    background_removal(image_8bit, out)


def _open(threshold: ndarray):
    kernel = numpy.ones((3, 3), numpy.uint8)
    temp_in = numpy.empty_like(threshold[0], dtype=numpy.uint8)
    temp_out = temp_in.copy()
    for z in range(threshold.shape[0]):
        temp_in[:] = threshold[z]
        cv2.morphologyEx(temp_in, cv2.MORPH_OPEN, kernel, dst=temp_out)
        threshold[z] = temp_out


def fill_threshold(threshold: ndarray):
    """Filling of all holes."""
    temp = numpy.empty_like(threshold[0])
    for z in range(threshold.shape[0]):
        _fill_threshold_2d(threshold[z], temp)


def _fill_threshold_2d(threshold: ndarray, temp_for_floodfill: ndarray):
    """Filling of all holes in a single 2D plane."""
    # https://www.learnopencv.com/filling-holes-in-an-image-using-opencv-python-c/
    temp_for_floodfill[:] = threshold

    # Mask used to flood filling.
    # Notice the size needs to be 2 pixels than the image.
    h, w = threshold.shape[:2]
    mask = numpy.zeros((h + 2, w + 2), numpy.uint8)

    # Floodfill from point (w-1, h-1) = bottom right
    cv2.floodFill(temp_for_floodfill, mask, (w - 1, h - 1), 255)

    # Invert floodfilled image, combine with threshold
    im_floodfill_inv = cv2.bitwise_not(temp_for_floodfill)
    threshold |= im_floodfill_inv
