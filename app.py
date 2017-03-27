import shutil
import sys

import skimage.io

from helpers import logger
from stages import region_proposal, text_region_extraction

LOGGER = logger.create_logger(__name__)


def get_new_image_dimensions(image):

    LOGGER.info("Calculating the new image dimensions ...")

    img = skimage.io.imread(image.name)
    width = len(img[0])
    height = len(img)

    if width * height < 256 * 256 * (0.95) and abs(width - height) <= 3:
        new_size = 512
    elif width * height < 220 * 220 * (1.11):
        new_size = 256
    elif width * height < 256 * 256:
        new_size = 256
    elif width * height > 512 * 512 * (0.99) and width < 800 and height < 800:
        new_size = 512
    elif width * height < 512 * 512 * (0.95) and width * height > 256 * 256 * (1.15):
        new_size = 512

    new_height = int(new_size * height / width)
    new_width = new_size

    return new_width, new_height


def get_text_regions(seal, new_width, new_height):
    candidate_regions = \
        region_proposal.region_search.get_candidate_regions(seal, new_width, new_height)
    grouped_regions = \
        region_proposal.region_grouping.group_candidate_regions(candidate_regions, new_width, new_height)
    text_regions, no_text_regions, both_regions = \
        text_region_extraction.region_classification.process_regions(seal, grouped_regions, new_width, new_height)
    formulated_text_regions = \
        text_region_extraction.text_region_formulation.process_regions(text_regions, no_text_regions, both_regions, new_width, new_height)

    return formulated_text_regions


def get_best_text_regions(seal, new_width, new_height):
    orig_image = skimage.io.imread(seal.name)
    orig_width = len(orig_image[0])
    orig_height = len(orig_image)

    all_dimensions = set([256, 512, orig_width])
    tried_dimensions = set()

    while True:
        tried_dimensions.add(new_width)
        text_regions = get_text_regions(seal, new_width, new_height)

        # min area check
        is_less_min_area = False
        for x, y, w, h in text_regions:
            if w * h < new_width * new_height * 0.20 and (w < new_width * 0.20 or h < new_height * 0.20):
                is_less_min_area = True

        if (len(text_regions) == 0 or is_less_min_area) and len(tried_dimensions) < 3:
            new_width = list(all_dimensions - tried_dimensions)[0]
            new_height = int(new_width * orig_height / orig_width)
            LOGGER.info("New size being tried: " + str(new_width))

        else:
            return text_regions

def process(image_path):
    seal = region_proposal.extract_seal.crop_white(image_path)
    new_width, new_height = get_new_image_dimensions(seal)
    best_text_regions = get_best_text_regions(seal, new_width, new_height)


if __name__ == "__main__":
    input_artifact_image_path = sys.argv[1]
    process(input_artifact_image_path)
