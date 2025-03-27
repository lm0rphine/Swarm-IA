# zones.py

# Zone de détection des movers en phase active (minicycle)
crop_region = (490, 260, 810, 580)  # x_min, y_min, x_max, y_max

# Coordonnées précises des 12 positions de filtre sur la plaque blanche (3x4)
plate_positions = [
    (238, 162, 246, 166),  # 1
    (273, 165, 277, 167),  # 2
    (303, 162, 309, 169),  # 3
    (240, 191, 241, 195),  # 4
    (271, 191, 275, 197),  # 5
    (301, 190, 308, 194),  # 6
    (236, 217, 238, 221),  # 7
    (273, 224, 267, 226),  # 8
    (304, 217, 307, 223),  # 9
    (236, 253, 231, 249),  # 10
    (270, 252, 263, 246),  # 11
    (297, 248, 305, 254),  # 12
]
