import skimage.io
import skimage.transform

from helpers import logger
from lib import selectivesearch

LOGGER = logger.create_logger(__name__)


def get_candidate_regions(image, width, height):
    LOGGER.info("Extracting the candidate regions ...")
    candidates = set()

    stage = 1
    for sc in [350, 450, 500]:
        for sig in [0.8]:
            for mins in [30, 60, 120]:
                img = skimage.io.imread(image.name)[:, :, :3]
                if not (height == len(img) and width == len(img[0])):
                    img = skimage.transform.resize(img, (height, width))

                _, regions = selectivesearch.selective_search(
                    img, scale=sc, sigma=sig, min_size=mins)

                for r in regions:
                    # excluding same rectangle (with different segments)
                    if r['rect'] in candidates:
                        continue

                    # excluding regions smaller than 2000 pixels
                    if r['size'] < 2000:  # TODO: Should not be hard coded, determine from image size
                        continue

                    # distorted rects
                    _, _, w, h = r['rect']
                    if w / h > 1.2 or h / w > 1.2:
                        continue

                    # rects covering entire seal image
                    if w >= (img.shape[0] - 1) * (0.7) and h >= (img.shape[1] - 1) * (0.7):
                        continue

                    candidates.add(r['rect'])

        LOGGER.info("Stage " + str(stage) + " Complete.")
        stage += 1

    return candidates
