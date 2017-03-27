import os

import numpy as np
import skimage.io
import skimage.transform

import caffe
from helpers.temp import TemporaryFile
from helpers import logger

LOGGER = logger.create_logger(__name__)


def get_region_crops(image, grouped_regions, new_width, new_height):
    img = skimage.io.imread(image.name)[:, :, :3]
    if not (new_height == len(img) and new_width == len(img[0])):
        img = skimage.transform.resize(img, (new_height, new_width))

    region_coords = list()
    region_crops = list()
    for x, y, w, h in grouped_regions:
        temp = TemporaryFile(".jpg")
        skimage.io.imsave(temp.name, img[y: y + h, x: x + w])
        region_crops.append(caffe.io.load_image(temp.name))
        region_coords.append((x, y, w, h))

    return region_coords, region_crops


def get_predictions(region_crops):
    if os.environ["IS_GPU"]:
        caffe.set_device(0)
        caffe.set_mode_gpu()
    else:
        caffe.set_mode_cpu()

    classifier = caffe.Classifier(os.path.join(os.environ["TEXT_NOTEXT_MODELS_DIR"], "deploy.prototxt"),
                                  os.path.join(os.environ["TEXT_NOTEXT_MODELS_DIR"], "weights.caffemodel"),
                                  mean=np.array([104, 117, 123], dtype='f4'),
                                  image_dims=[224, 224],
                                  raw_scale=255.0,
                                  channel_swap=[2, 1, 0])

    LOGGER.info("Classifying " + len(region_crops) + " inputs.")

    predictions = classifier.predict(region_crops)

    return predictions


def classify_regions(region_coords, region_crops):
    text_regions = set()
    no_text_regions = set()
    both_regions = set()
    classes = np.array([0, 1, 2])

    try:
        predictions = get_predictions(region_crops)
        for i, prediction in enumerate(predictions):
            idx = list((-prediction).argsort())
            prediction = classes[np.array(idx)]

            if prediction[0] == 1 or prediction[0] == 2:
                text_regions.add(region_coords[i])
            elif prediction[0] == 0:
                no_text_regions.add(region_coords[i])
            if prediction[0] == 2:
                both_regions.add(region_coords[i])
    except:
        LOGGER.info("Failed to classify regions!")

    return text_regions, no_text_regions, both_regions


def process_regions(image, grouped_regions, new_width, new_height):
    region_coords, region_crops = \
        get_region_crops(image, grouped_regions, new_width, new_height)
    text_regions, no_text_regions, both_regions = \
        classify_regions(region_coords, region_crops)

    return text_regions, no_text_regions, both_regions
