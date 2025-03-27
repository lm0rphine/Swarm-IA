# utils.py

def bbox_in_crop(bbox, crop):
    x_min, y_min, x_max, y_max = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
    return crop[0] <= x_min <= crop[2] and crop[1] <= y_min <= crop[3]

def bbox_in_zone(bbox, zone):
    bx_min, by_min, bx_max, by_max = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
    zx_min, zy_min, zx_max, zy_max = zone
    return not (bx_max < zx_min or bx_min > zx_max or by_max < zy_min or by_min > zy_max)

def assign_mover_ids(movers_bboxes, ids):
    # Trie les movers de gauche à droite
    movers_bboxes = sorted(movers_bboxes, key=lambda b: b[0])
    assigned = {}
    for i, bbox in enumerate(movers_bboxes):
        if i < len(ids):
            assigned[ids[i]] = bbox
    return assigned
