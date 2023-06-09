# Update:
# thêm def create_annotation_info_direction để có thể tạo data có kèm theo angle (tính direction) khi cần!!!
#!/usr/bin/env python3

import os
import re
import datetime
import numpy as np
from itertools import groupby
from skimage import measure
from PIL import Image
from pycocotools import mask
import matplotlib.pyplot as plt
import cv2

convert = lambda text: int(text) if text.isdigit() else text.lower()
natrual_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]

def resize_array(array, new_size):
    image = Image.fromarray(array)
    image = image.resize(new_size)
    return np.asarray(image)

def close_contour(contour):
    if not np.array_equal(contour[0], contour[-1]):
        contour = np.vstack((contour, contour[0]))
    return contour

def binary_mask_to_rle(binary_mask):
    rle = {'counts': [], 'size': list(binary_mask.shape)}
    counts = rle.get('counts')
    for i, (value, elements) in enumerate(groupby(binary_mask.ravel(order='F'))):
        if i == 0 and value == 1:
                counts.append(0)
        counts.append(len(list(elements)))

    return rle

def binary_mask_to_polygon(binary_mask, tolerance=0):
    """Converts a binary mask to COCO polygon representation

    Args:
        binary_mask: a 2D binary numpy array where '1's represent the object
        tolerance: Maximum distance from original points of polygon to approximated
            polygonal chain. If tolerance is 0, the original coordinate array is returned.

    """
    polygons = []
    # pad mask to close contours of shapes which start and end at an edge
    padded_binary_mask = np.pad(binary_mask, pad_width=1, mode='constant', constant_values=0)
    # print("padded_binary_mask", padded_binary_mask)
    contours = measure.find_contours(padded_binary_mask, 0.5)
    # print("contours123:", len(contours))
    max_area = 0
    max_ctr = None
    if len(contours) > 1:
        for cnt in contours:
            area = cv2.contourArea(cnt.astype(np.int))
            if area > max_area:
                max_ctr = cnt
                max_area = area
    # print("contours 11111", max_ctr)
    if max_ctr is None:
        contours = contours
    else: 
        contours = [max_ctr]
    # print("contours:", len(contours))
    # fig, ax = plt.subplots()
    # ax.imshow(image_bir, interpolation='nearest', cmap=plt.cm.gray)
    # for n, contour in enumerate(contours):
    #     ax.plot(contour[:, 1], contour[:, 0], linewidth=2)
    # ax.axis('image')
    # ax.set_xticks([])
    # ax.set_yticks([])
    # plt.show()
    contours = np.subtract(contours, 1)
    for contour in contours:
        contour = close_contour(contour)
        contour = measure.approximate_polygon(contour, tolerance)
        if len(contour) < 3:
            continue
        contour = np.flip(contour, axis=1)
        segmentation = contour.ravel().tolist()
        # after padding and subtracting 1 we may get -0.5 points in our segmentation 
        segmentation = [0 if i < 0 else i for i in segmentation]
        polygons.append(segmentation)

    return polygons

def create_image_info(image_id, file_name, image_size, 
                      date_captured=datetime.datetime.utcnow().isoformat(' '),
                      license_id=1, coco_url="", flickr_url=""):

    image_info = {
            "id": image_id,
            "file_name": file_name,
            "width": image_size[0],
            "height": image_size[1],
            "date_captured": date_captured,
            "license": license_id,
            "coco_url": coco_url,
            "flickr_url": flickr_url
    }

    return image_info

def create_annotation_info(annotation_id, image_id, category_info, binary_mask, image_size, tolerance=0):

    binary_mask = resize_array(binary_mask, image_size)
    # print("binary_mask", binary_mask.shape)
    binary_mask_encoded = mask.encode(np.asfortranarray(binary_mask.astype(np.uint8)))
    bounding_box = mask.toBbox(binary_mask_encoded)
    area = mask.area(binary_mask_encoded)

    if area < 1:
        return None

    if category_info["is_crowd"]:
        is_crowd = 1
        segmentation = binary_mask_to_rle(binary_mask)
    else :
        is_crowd = 0
        segmentation = binary_mask_to_polygon(binary_mask,  tolerance)
        if not segmentation:
            return None

    annotation_info = {
        "id": annotation_id,
        "image_id": image_id,
        "category_id": category_info["id"],
        "iscrowd": is_crowd,
        "area": area.tolist(),
        "bbox": bounding_box.tolist(),
        "segmentation": segmentation,
        "width": binary_mask.shape[1],
        "height": binary_mask.shape[0],
    } 

    return annotation_info


def create_annotation_info_direction(annotation_id, image_id, category_info, binary_mask, image_size, angle, tolerance=0):
    binary_mask = resize_array(binary_mask, image_size)
    #print("binary_mask:",binary_mask)
    binary_mask_encoded = mask.encode(np.asfortranarray(binary_mask.astype(np.uint8)))
    bounding_box = mask.toBbox(binary_mask_encoded)
    #print("bounding_box = ", bounding_box)
    #bbox_ = bounding_box.tolist()
    #print("bounding_box.tolist() = ", bbox_)
    #print("bbox_[0] = ", bbox_[0])
    area = mask.area(binary_mask_encoded)

    if area < 1:
        return None

    if category_info["is_crowd"]:
        is_crowd = 1
        segmentation = binary_mask_to_rle(binary_mask)
    else :
        is_crowd = 0
        segmentation = binary_mask_to_polygon(binary_mask, tolerance)
        #print("segmentation", segmentation)
        if not segmentation:
            return None

    annotation_info_direction = {
        "id": annotation_id,
        "image_id": image_id,
        "category_id": category_info["id"],
        "iscrowd": is_crowd,
        "area": area.tolist(),
        "bbox": bounding_box.tolist(),
        "segmentation": segmentation,
        "width": binary_mask.shape[1],
        "height": binary_mask.shape[0],
        "angle": angle,
    } 
    return annotation_info_direction

def create_annotation_info_angle_classification(annotation_id, image_id, category_info, binary_mask, image_size, tolerance=0):
    binary_mask = resize_array(binary_mask, image_size)
    #print("binary_mask:",binary_mask)
    binary_mask_encoded = mask.encode(np.asfortranarray(binary_mask.astype(np.uint8)))
    bounding_box = mask.toBbox(binary_mask_encoded)
    #print("bounding_box = ", bounding_box)
    #bbox_ = bounding_box.tolist()
    #print("bounding_box.tolist() = ", bbox_)
    #print("bbox_[0] = ", bbox_[0])
    area = mask.area(binary_mask_encoded)

    if area < 1:
        return None

    if category_info["is_crowd"]:
        is_crowd = 1
        segmentation = binary_mask_to_rle(binary_mask)
    else :
        is_crowd = 0
        segmentation = binary_mask_to_polygon(binary_mask, tolerance)
        #print("segmentation", segmentation)
        if not segmentation:
            return None

    annotation_info = {
        "id": annotation_id,
        "image_id": image_id,
        "category_id": category_info["id"],
        "angle_id": category_info["angle"],
        "iscrowd": is_crowd,
        "area": area.tolist(),
        "bbox": bounding_box.tolist(),
        "segmentation": segmentation,
        "width": binary_mask.shape[1],
        "height": binary_mask.shape[0],
    } 
    return annotation_info
