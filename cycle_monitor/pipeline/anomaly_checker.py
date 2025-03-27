# anomaly_checker.py

import time

def check_anomalies(state, filters_on_plate, mover_full_crop_bboxes, mover_empty_crop_bboxes, last_activity_time):
    anomalies = []
    now = time.time()

    # Temps anormalement long pour une phase
    if state["phase"] == "charging" and now - state["start_charge"] > 10:
        anomalies.append("⏳ Chargement trop long")
    if state["phase"] == "decharging" and now - state["start_decharge"] > 10:
        anomalies.append("⏳ Déchargement trop long")

    # Aucun filtre retiré après démarrage
    if filters_on_plate == 12 and not state["init_phase"] and state["minicycle_count"] > 1:
        anomalies.append("🧪 Aucun filtre retiré depuis le début")

    # Mover incohérent
    if state["phase"] == "charging" and len(mover_empty_crop_bboxes) > 0:
        anomalies.append("📦 Mover vide détecté pendant chargement")
    if state["phase"] == "decharging" and len(mover_full_crop_bboxes) > 0:
        anomalies.append("📦 Mover plein détecté pendant déchargement")

    # Absence prolongée d'activité
    if now - last_activity_time > 15:
        anomalies.append("🚫 Aucune activité détectée depuis 15 secondes")

    return anomalies
