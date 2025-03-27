# zones.py

# Zone de détection des movers en phase active (minicycle)
crop_region = (490, 260, 810, 580)  # x_min, y_min, x_max, y_max

# Coordonnées des 12 positions de filtre sur la plaque blanche (3 lignes x 4 colonnes)
plate_positions = [
    (150, 100, 180, 130), (185, 100, 215, 130), (220, 100, 250, 130), (255, 100, 285, 130),
    (150, 135, 180, 165), (185, 135, 215, 165), (220, 135, 250, 165), (255, 135, 285, 165),
    (150, 170, 180, 200), (185, 170, 215, 200), (220, 170, 250, 200), (255, 170, 285, 200)
]
