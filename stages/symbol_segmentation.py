import os

import numpy as np
import skimage.color
import skimage.io
import skimage.morphology
import skimage.transform
from scipy import ndimage
from skimage.filters import gaussian_filter, threshold_otsu

from helpers.temp import TemporaryFile, TemporaryDirectory


def extend_rect(r):
    return (min([i[0] for i in r]), min([i[1] for i in r]), max([i[0] + i[2] for i in r]) - min([i[0] for i in r]), max([i[1] + i[3] for i in r]) - min([i[1] for i in r]))


def remove_contained_regions(candidates):
    refined_regions = set()
    for x, y, w, h in candidates:
        candidates_complement = set(candidates)
        candidates_complement.remove((x, y, w, h))
        is_not_contained = []
        for x1, y1, w1, h1 in candidates_complement:
            a = {'x1': x, 'y1': y, 'x2': x + w, 'y2': y + h, 'w': w, 'h': h}
            b = {'x1': x1, 'y1': y1, 'x2': x1 + w1, 'y2': y1 + h1, 'w': w1, 'h': h1}

            # overlap between a and b
            area_a = a['w'] * a['h']
            area_b = b['w'] * b['h']
            area_intersection = np.max([0, np.min([a['x2'], b['x2']]) - np.max([a['x1'], b['x1']])]) * \
                np.max([0, np.min([a['y2'], b['y2']]) - np.max([a['y1'], b['y1']])])

            area_union = area_a + area_b - area_intersection
            overlap_ab = float(area_intersection) / float(area_union)

            if overlap_ab > 0.0:
                if x1 <= x and y1 <= y and x1 + w1 >= x + w and y1 + h1 >= y + h:
                    is_not_contained.append(False)
                else:
                    is_not_contained.append(True)
            else:
                is_not_contained.append(True)

        if all(is_not_contained):
            refined_regions.add((x, y, w, h))

    return refined_regions


def draw_superbox(refined_regions, old_superboxes=[]):
    no_overlap = []
    draw_superbox_candidates = []

    superboxes = set()

    if not old_superboxes:
        draw_superbox_candidates = old_superboxes
    else:
        draw_superbox_candidates = refined_regions

    base_list = list(draw_superbox_candidates)
    base_set = set(draw_superbox_candidates)

    # (x1,y1) top-left coord, (x2,y2) bottom-right coord, (w,h) size
    while base_list:
        x1, y1, w1, h1 = base_list[0]

        if len(base_list) == 1:  # super box
            superboxes.add((x1, y1, w1, h1))

        base_list.remove((x1, y1, w1, h1))

        overlap = set()
        base_set.remove((x1, y1, w1, h1))
        for x2, y2, w2, h2 in base_set:
            a = {'x1': x1, 'y1': y1, 'x2': x1 + w1, 'y2': y1 + h1, 'w': w1, 'h': h1}
            b = {'x1': x2, 'y1': y2, 'x2': x2 + w2, 'y2': y2 + h2, 'w': w2, 'h': h2}

            # overlap between A and B
            area_a = a['w'] * a['h']
            area_b = b['w'] * b['h']
            area_intersection = np.max([0, np.min([a['x2'], b['x2']]) - np.max([a['x1'], b['x1']])]) * \
                np.max([0, np.min([a['y2'], b['y2']]) - np.max([a['y1'], b['y1']])])

            # area_union = area_a + area_b - area_intersection
            # overlap_ab = float(area_intersection) / float(area_union)

            overlap_a = float(area_intersection) / float(area_a)
            overlap_b = float(area_intersection) / float(area_b)

            if overlap_a >= 0.15 or overlap_b >= 0.15:
                overlap.add((b['x1'], b['y1'], b['w'], b['h']))

        if overlap:  # overlap
            base_set = base_set - overlap
            base_list = [bl for bl in base_list if bl not in overlap]
            overlap.add((a['x1'], a['y1'], a['w'], a['h']))

            superboxes.add((min([i[0] for i in overlap]), min([i[1] for i in overlap]), max([i[0] + i[2] for i in overlap]) -
                            min([i[0] for i in overlap]), max([i[1] + i[3] for i in overlap]) - min([i[1] for i in overlap])))

            no_overlap.append(False)
        else:  # no overlap
            superboxes.add((x1, y1, w1, h1))
            no_overlap.append(True)

    if all(no_overlap):
        return superboxes
    else:
        draw_superbox(refined_regions, superboxes)
        return superboxes


def extend_superbox(superboxes):
    extended_superboxes = set()
    processed = set()

    for x, y, w, h in superboxes:
        if (x, y, w, h) not in processed:
            group = set()

            group.add((x, y, w, h))
            for x1, y1, w1, h1 in superboxes:
                if x1 >= x and (w1 + x1) <= w + x:
                    group.add((x1, y1, w1, h1))
                    processed.add((x1, y1, w1, h1))

            extended_superboxes.add(extend_rect(group))

    return remove_contained_regions(extended_superboxes)


def get_candidate_symbol_regions(image, text_regions, updated_width, updated_height):
    img = skimage.io.imread(image.name)[:, :, :3]
    if not (updated_height == len(img) and updated_width == len(img[0])):
        img = skimage.transform.resize(img, (updated_height, updated_width))

    symbol_regions = dict()
    for x, y, w, h in text_regions:
        text_region_image = img[y: y + h, x: x + w]
        text_region_image_width = len(text_region_image[0])
        text_region_image_height = len(text_region_image)

        text_region_gray_image = skimage.color.rgb2gray(text_region_image)
        text_region_binary_image = image <= threshold_otsu(text_region_gray_image)

        temp = TemporaryFile(".png")
        skimage.io.imsave(temp.name, text_region_binary_image)
        text_region_binary_image = skimage.io.imread(temp.name)

        text_region_blurred_image = gaussian_filter(text_region_binary_image, sigma=3.5)
        text_region_blobs = text_region_blurred_image > text_region_blurred_image.mean()

        text_region_labels = skimage.morphology.label(text_region_blobs, neighbors=4)

        symbol_blobs = ndimage.find_objects(text_region_labels)
        candidate_symbol_regions = set()

        for c1, c2 in symbol_blobs:
            if (c2.stop - c2.start) * c1.stop - c1.start > (text_region_image.shape[0] * text_region_image.shape[1]) * (0.026):
                if (c2.stop - c2.start) * c1.stop - c1.start < (text_region_image.shape[0] * text_region_image.shape[1]) * (0.90):
                    candidate_symbol_regions.add(
                        (c2.start, c1.start, c2.stop - c2.start, c1.stop - c1.start))

        symbol_regions[str((x, y, w, h))] = dict()
        symbol_regions[str((x, y, w, h))]["image"] = text_region_image
        symbol_regions[str((x, y, w, h))]["regions"] = candidate_symbol_regions
        symbol_regions[str((x, y, w, h))]["width"] = text_region_image_width
        symbol_regions[str((x, y, w, h))]["height"] = text_region_image_height

    return symbol_regions


def process_candidate_symbol_regions(symbol_regions):
    for text_region in symbol_regions:
        candidate_symbol_regions = symbol_regions[text_region]["regions"]
        refined_regions = remove_contained_regions(candidate_symbol_regions)
        superboxes = draw_superbox(refined_regions)
        refined_extended_superboxes = extend_superbox(superboxes)

        symbol_regions[text_region]["refined_regions"] = refined_extended_superboxes

    return symbol_regions


def get_symbols(image, text_regions, updated_width, updated_height):
    symbol_regions = get_candidate_symbol_regions(image, text_regions, updated_width, updated_height)
    symbol_regions = process_candidate_symbol_regions(symbol_regions)

    symbols = list()
    for text_region in symbol_regions:
        for x, y, w, h in symbol_regions[text_region]["refined_regions"]:
            symbols.append([(x, y, w, h), symbol_regions[text_region]["image"][y: y + h, x: x + w]])

    # sort the symbols according to horizontal order
    symbols = sorted(symbols, key=lambda x: x[0][0])

    # save all the symbols in a TemporaryDirectory
    symbols_dir = TemporaryDirectory()

    for i, symbol in enumerate(symbols):
        skimage.io.imsave(os.path.join(symbols_dir.name, i + ".jpg"), symbol[1])

    return symbols_dir
