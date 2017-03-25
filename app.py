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


def process(image_path):
    seal = region_proposal.extract_seal.crop_white(image_path)
    new_width, new_height = get_new_image_dimensions(seal)

    candidate_regions = region_proposal.region_search.get_candidate_regions(seal, new_width, new_height)
    grouped_regions = region_proposal.region_grouping.group_candidate_regions(candidate_regions, new_width, new_height)
    text_regions, no_text_regions, both_regions = \
        text_region_extraction.region_classification.process_regions(seal, grouped_regions, new_width, new_height)


if __name__ == "__main__":
    input_artifact_image_path = sys.argv[1]
    process(input_artifact_image_path)
