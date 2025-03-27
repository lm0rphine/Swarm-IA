# inventory_manager.py

inventory = {
    "filtres_charges": 0,
    "filtres_decharges": 0,
    "total_filtres_manipules": 0
}

# Heatmap des cases (index 0 à 11)
plate_usage = [0] * 12

def update_inventory(phase):
    if phase == "charging":
        inventory["filtres_charges"] += 4
    elif phase == "decharging":
        inventory["filtres_decharges"] += 4
    inventory["total_filtres_manipules"] += 4

def update_heatmap(filter_bboxes, plate_positions):
    for i, zone in enumerate(plate_positions):
        for bbox in filter_bboxes:
            if bbox_in_zone(bbox, zone):
                plate_usage[i] += 1
                break

def reset_inventory():
    inventory["filtres_charges"] = 0
    inventory["filtres_decharges"] = 0
    inventory["total_filtres_manipules"] = 0
    global plate_usage
    plate_usage = [0] * 12

def bbox_in_zone(bbox, zone):
    bx_min, by_min, bx_max, by_max = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
    zx_min, zy_min, zx_max, zy_max = zone
    return not (bx_max < zx_min or bx_min > zx_max or by_max < zy_min or by_min > zy_max)
