import os

import numpy as np
import skimage.io
import skimage.transform

import caffe
from helpers import logger

LOGGER = logger.create_logger(__name__)


def get_symbol_images(symbols_dir):
    symbols = list()
    symbols_list = sorted(os.listdir(symbols_dir.name), key=lambda i: int(os.path.splitext(i)[0]))
    for filename in symbols_list:
        image_path = os.path.join(symbols_dir.name, filename)
        symbols.append([image_path, caffe.io.load_image(image_path, color=False)])

    return symbols


def get_symbol_classifications(symbols):
    if os.environ["IS_GPU"]:
        caffe.set_device(0)
        caffe.set_mode_gpu()
    else:
        caffe.set_mode_cpu()

    classifier = caffe.Classifier(os.path.join(os.environ["JAR_NOJAR_MODELS_DIR"], "deploy.prototxt"),
                                  os.path.join(os.environ["JAR_NOJAR_MODELS_DIR"], "weights.caffemodel"),
                                  image_dims=[64, 64],
                                  raw_scale=255.0)

    LOGGER.info("Classifying " + str(len(symbols)) + " inputs.")

    predictions = classifier.predict([s[1] for s in symbols])

    symbol_sequence = list()
    classes = np.array([0, 1])

    for i, prediction in enumerate(predictions):
        idx = list((-prediction).argsort())
        prediction = classes[np.array(idx)]

        if prediction[0] == 1:
            symbol_sequence.append([symbols[i], "jar"])
        elif prediction[0] == 0:
            symbol_sequence.append([symbols[i], "no-jar"])

    return symbol_sequence


def process_symbols(symbols_dir):
    symbols = get_symbol_images(symbols_dir)
    symbol_sequence = get_symbol_classifications(symbols)

    return symbol_sequence
