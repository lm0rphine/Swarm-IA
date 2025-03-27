# detection_app.py

import time
import cv2
import hailo
from hailo_apps_infra.hailo_rpi_common import (
    get_caps_from_pad,
    get_numpy_from_buffer,
)
from gi.repository import Gst

from .state_manager import state
from .zones import crop_region, plate_positions
from .utils import bbox_in_crop, bbox_in_zone
from .inventory_manager import update_inventory, update_heatmap
from .anomaly_checker import check_anomalies
from .mover_tracker import MoverTracker

tracker = MoverTracker()

class user_app_callback_class:
    def __init__(self):
        self.frame_count = 0
        self.use_frame = True
        self.frame = None
        self.last_activity_time = time.time()

    def increment(self):
        self.frame_count += 1

    def get_count(self):
        return self.frame_count

    def set_frame(self, frame):
        self.frame = frame

    def new_function(self):
        return "Cycle Tracker"

def app_callback(pad, info, user_data):
    buffer = info.get_buffer()
    if buffer is None:
        return Gst.PadProbeReturn.OK

    user_data.increment()
    format, width, height = get_caps_from_pad(pad)
    frame = None

    if user_data.use_frame and format and width and height:
        frame = get_numpy_from_buffer(buffer, format, width, height)

    roi = hailo.get_roi_from_buffer(buffer)
    detections = roi.get_objects_typed(hailo.HAILO_DETECTION)

    now = time.time()
    label_counts = {"filter": 0, "mover_full": 0, "mover_empty": 0}
    mover_full_bboxes = []
    mover_empty_bboxes = []
    mover_full_crop_bboxes = []
    mover_empty_crop_bboxes = []
    filter_bboxes = []

    for det in detections:
        label = det.get_label()
        bbox = det.get_bbox()
        if label in label_counts:
            label_counts[label] += 1
        if label == "mover_full":
            mover_full_bboxes.append(bbox)
            if bbox_in_crop(bbox, crop_region):
                mover_full_crop_bboxes.append(bbox)
        elif label == "mover_empty":
            mover_empty_bboxes.append(bbox)
            if bbox_in_crop(bbox, crop_region):
                mover_empty_crop_bboxes.append(bbox)
        elif label == "filter":
            filter_bboxes.append(bbox)

    filters_on_plate = 0
    for zone in plate_positions:
        for bbox in filter_bboxes:
            if bbox_in_zone(bbox, zone):
                filters_on_plate += 1
                break

    print(f"🧪 Filtres sur la plaque : {filters_on_plate}/12")
    update_heatmap(filter_bboxes, plate_positions)

    if state["init_phase"]:
        if filters_on_plate < 12 and len(mover_empty_crop_bboxes) == 0 and len(mover_full_crop_bboxes) >= 4:
            state["init_loaded_groups"] += 1
            print(f"➡️ Initialisation: groupe {state['init_loaded_groups']} chargé")
            if state["init_loaded_groups"] >= 3:
                state["init_phase"] = False
                print("🟢 Début du cycle normal !")
        return Gst.PadProbeReturn.OK

    if len(mover_full_crop_bboxes) >= 4 and state["phase"] == "idle":
        state["phase"] = "decharging"
        state["start_decharge"] = now
        state["minicycle_count"] += 1
        if state["minicycle_count"] % 3 == 1:
            state["cycle_start_time"] = now
        print(f"\n▶️ Début déchargement (minicycle {state['minicycle_count']})")
        user_data.last_activity_time = now

    elif len(mover_full_crop_bboxes) == 0 and state["phase"] == "decharging":
        state["end_decharge"] = now
        state["phase"] = "charging"
        state["start_charge"] = now
        print("✅ Fin déchargement / Début chargement")
        update_inventory("decharging")
        user_data.last_activity_time = now

    elif len(mover_empty_crop_bboxes) >= 4 and state["phase"] == "charging":
        state["end_charge"] = now
        state["phase"] = "waiting_departure"
        print("✅ Fin chargement / En attente de départ movers")
        update_inventory("charging")
        user_data.last_activity_time = now

    elif len(mover_empty_crop_bboxes) == 0 and state["phase"] == "waiting_departure":
        minicycle_time = state["end_charge"] - state["start_decharge"]
        print(f"🌀 Minicycle terminé. Durée : {minicycle_time:.2f} sec")

        state["mover_number_map"]["current"] = state["mover_number_map"]["waiting_next"]
        state["mover_number_map"]["waiting_next"] = state["mover_number_map"]["after_next"]
        state["mover_number_map"]["after_next"] = [1, 2, 3, 4]

        state["phase"] = "idle"

        if state["minicycle_count"] % 3 == 0:
            state["cycle_count"] += 1
            if state["cycle_start_time"]:
                full_cycle_time = now - state["cycle_start_time"]
                print(f"✅✅ Cycle complet #{state['cycle_count']} terminé. Durée : {full_cycle_time:.2f} sec\n")

    anomalies = check_anomalies(state, filters_on_plate, mover_full_crop_bboxes, mover_empty_crop_bboxes, user_data.last_activity_time)
    for anomaly in anomalies:
        print("❗", anomaly)

    if user_data.use_frame and frame is not None:
        cv2.putText(frame, user_data.new_function(), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        mover_bboxes = mover_full_bboxes + mover_empty_bboxes
        tracked = tracker.match_bboxes(mover_bboxes)
        for mover_id, bbox in tracked.items():
            x_min, y_min = int(bbox[0]), int(bbox[1])
            cv2.putText(frame, f"#{mover_id}", (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
            cv2.rectangle(frame, (x_min, int(bbox[1])), (int(bbox[2]), int(bbox[3])), (255, 0, 0), 2)

        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        user_data.set_frame(frame)

    return Gst.PadProbeReturn.OK
