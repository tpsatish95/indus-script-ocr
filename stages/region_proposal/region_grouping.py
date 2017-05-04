import numpy as np

from helpers import logger

LOGGER = logger.create_logger(__name__)


def mean_rect(r):
    return (min([i[0] for i in r]), min([i[1] for i in r]), max([i[0] + i[2] for i in r]) - min([i[0] for i in r]), max([i[1] + i[3] for i in r]) - min([i[1] for i in r]))


def extend_rect(r):
    return (min([i[0] for i in r]), min([i[1] for i in r]), max([i[0] + i[2] for i in r]) - min([i[0] for i in r]), max([i[3] for i in r]))


def merge(candidates, width, height):
    merged_candidates = set()
    processed = set()

    threshold = int(((width + height) / 2) * (0.14))
    for x, y, w, h in candidates:
        if (x, y, w, h) not in processed:
            group = set()
            group.add((x, y, w, h))
            for x1, y1, w1, h1 in candidates:
                if abs(x1 - x) <= threshold and abs(y1 - y) <= threshold and abs(w1 - w) <= threshold and abs(h1 - h) <= threshold:
                    group.add((x1, y1, w1, h1))
                    processed.add((x1, y1, w1, h1))
            merged_candidates.add(mean_rect(group))

    return merged_candidates


def contains_remove(merged_candidates):
    refined_merged_candidates = set()
    for x, y, w, h in merged_candidates:
        is_contained = False
        merged_candidates_copy = set(merged_candidates)
        merged_candidates_copy.remove((x, y, w, h))
        for x1, y1, w1, h1 in merged_candidates_copy:
            if x1 >= x and y1 >= y and x1 + w1 <= x + w and y1 + h1 <= y + h:
                is_contained = True
                break

        if not is_contained:
            refined_merged_candidates.add((x, y, w, h))

    return refined_merged_candidates


def draw_superbox(refined_merged_candidates, old_superboxes=[]):
    no_overlap = []
    draw_superbox_candidates = []

    superboxes = set()

    if not old_superboxes:
        draw_superbox_candidates = old_superboxes
    else:
        draw_superbox_candidates = refined_merged_candidates

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

            if overlap_a >= 0.40 or overlap_b >= 0.40:
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
        draw_superbox(refined_merged_candidates, superboxes)
        return superboxes


def extend_superbox(superboxes, width, height):
    extended_superboxes = set()
    processed = set()

    threshold = ((width + height) / 2) * (0.06)
    for x, y, w, h in superboxes:
        if (x, y, w, h) not in processed:
            group = set()

            group.add((x, y, w, h))
            for x1, y1, w1, h1 in superboxes:
                if abs(y1 - y) <= threshold and abs(h1 - h) <= threshold:
                    group.add((x1, y1, w1, h1))
                    processed.add((x1, y1, w1, h1))

            extended_superboxes.add(extend_rect(group))

    return extended_superboxes


def group_candidate_regions(candidates, width, height):
    merged_candidates = merge(candidates, width, height)
    LOGGER.info(merged_candidates)
    refined_merged_candidates = contains_remove(merged_candidates)
    LOGGER.info(refined_merged_candidates)
    superboxes = draw_superbox(refined_merged_candidates)
    LOGGER.info(superboxes)
    extended_superboxes = extend_superbox(superboxes, width, height)
    LOGGER.info(extended_superboxes)

    return extended_superboxes
