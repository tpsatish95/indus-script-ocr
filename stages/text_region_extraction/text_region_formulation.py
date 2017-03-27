import numpy as np


def extend_text_rect(l):
    return (min([i[0] for i in l]), min([i[1] for i in l]), max([i[0] + i[2] for i in l]) - min([i[0] for i in l]), max([i[3] for i in l]))


def refine_text_regions(text_regions, width, height):
    refined_text_regions = set()
    processed = set()

    threshold = ((width + height) / 2) * (0.25)
    for x, y, w, h in text_regions:
        if (x, y, w, h) not in processed:
            group = set()
            group.add((x, y, w, h))
            for x1, y1, w1, h1 in text_regions:
                if abs(y1 - y) <= threshold and abs(h1 - h) <= threshold:
                    group.add((x1, y1, w1, h1))
                    processed.add((x1, y1, w1, h1))
            refined_text_regions.add(extend_text_rect(group))

    return refined_text_regions


def trim_text_regions(refined_text_regions, no_text_regions, both_regions):
    trimmed_text_regions = set()
    unwanted_regions = no_text_regions.union(both_regions)

    for x, y, w, h in refined_text_regions:
        a = {'x1': x, 'y1': y, 'x2': x + w, 'y2': y + h, 'w': w, 'h': h}
        for x1, y1, w1, h1 in unwanted_regions:
            b = {'x1': x1, 'y1': y1, 'x2': x1 + w1, 'y2': y1 + h1, 'w': w1, 'h': h1}

            # overlap between a and b
            area_a = a['w'] * a['h']
            area_b = b['w'] * b['h']
            area_intersection = np.max([0, np.min([a['x2'], b['x2']]) - np.max([a['x1'], b['x1']])]) * \
                np.max([0, np.min([a['y2'], b['y2']]) - np.max([a['y1'], b['y1']])])

            area_union = area_a + area_b - area_intersection
            overlap_ab = float(area_intersection) / float(area_union)

            is_overlap = False
            ax1, ay1, aw, ah = a['x1'], a['y1'], a['w'], a['h']

            if overlap_ab > 0.0:
                if a['x1'] > b['x1'] and abs(b['x1'] + b['w'] - a['x1']) < a['w'] * 0.20:  # b is left to a
                    ax1 = b['x1'] + b['w']
                    is_overlap = True
                if a['y1'] < b['y1'] and abs(a['y1'] - b['y1']) > a['h'] * 0.70:  # b is bottom to a
                    ah = a['h'] - (a['y1'] + a['h'] - b['y1'])
                    is_overlap = True
                # if a['y1'] > b['y1']: # b is top to a
                #     ay1 = b['y1'] + b['h']
                # if a['x1'] < b['x1']: # b is right to a
                #     aw = a['w'] - (a['x1'] + a['w'] - b['x1'])
                # if a['y1'] < b['y1']: # b is bottom to a
                #     ah = a['h'] - (a['y1'] + a['h'] - b['y1'])
                # REPLACE by Cohen Sutherland algo

                a['x1'], a['y1'], a['w'], a['h'] = ax1, ay1, aw, ah
                trimmed_text_regions.add((a['x1'], a['y1'], a['w'], a['h']))

            if is_overlap:
                break

        trimmed_text_regions.add((a['x1'], a['y1'], a['w'], a['h']))

    return trimmed_text_regions


def extend_text_regions(refined_text_regions, both_regions):
    extended_text_regions = set()

    for x, y, w, h in refined_text_regions:
        a = {'x1': x, 'y1': y, 'x2': x + w, 'y2': y + h, 'w': w, 'h': h}
        for x1, y1, w1, h1 in both_regions:
            b = {'x1': x1, 'y1': y1, 'x2': x1 + w1, 'y2': y1 + h1, 'w': w1, 'h': h1}

            # overlap between a and b
            area_a = a['w'] * a['h']
            area_b = b['w'] * b['h']
            area_intersection = np.max([0, np.min([a['x2'], b['x2']]) - np.max([a['x1'], b['x1']])]) * \
                np.max([0, np.min([a['y2'], b['y2']]) - np.max([a['y1'], b['y1']])])

            area_union = area_a + area_b - area_intersection
            overlap_ab = float(area_intersection) / float(area_union)

            is_overlap = False
            ax1, ay1, aw, ah = a['x1'], a['y1'], a['w'], a['h']
            if overlap_ab > 0.0:
                if a['x1'] > b['x1'] and abs(b['x1'] + b['w'] - a['x1']) < a['w'] * 0.20:  # b is left to a
                    ax1 = b['x1']
                    aw = a['x1'] + a['w'] - b['x1']
                    is_overlap = True
                # if a['y1'] < b['y1'] and abs(a['y1'] - b['y1']) > a['h']*0.70: # b is bottom to a
                #     ah = a['h'] - (a['y1'] + a['h'] - b['y1'])
                # if a['y1'] > b['y1']: # b is top to a
                #     ay1 = b['y1'] + b['h']
                if a['x1'] < b['x1']:  # b is right to a
                    aw = b['x1'] + b['w'] - a['x1']
                    is_overlap = True
                # if a['y1'] < b['y1']: # b is bottom to a
                #     ah = a['h'] - (a['y1'] + a['h'] - b['y1'])
                # REPLACE by Cohen Sutherland algo

                a['x1'], a['y1'], a['w'], a['h'] = ax1, ay1, aw, ah
                extended_text_regions.add((a['x1'], a['y1'], a['w'], a['h']))
            if is_overlap:
                break
        extended_text_regions.add((a['x1'], a['y1'], a['w'], a['h']))
    extended_text_regions = extended_text_regions - both_regions  # CHANGE this line

    return extended_text_regions


def process_regions(text_regions, no_text_regions, both_regions, width, height):
    refined_text_regions = refine_text_regions(text_regions, width, height)
    trimmed_text_regions = trim_text_regions(refined_text_regions, no_text_regions, both_regions)
    extended_text_regions = extend_text_regions(refined_text_regions, both_regions)

    return extended_text_regions
