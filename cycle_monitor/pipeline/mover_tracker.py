# mover_tracker.py

import numpy as np
from scipy.optimize import linear_sum_assignment

class MoverTracker:
    def __init__(self, max_distance=50):
        self.tracked_movers = {}  # mover_id: bbox
        self.next_id = 1
        self.max_distance = max_distance

    def iou(self, boxA, boxB):
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])

        interArea = max(0, xB - xA) * max(0, yB - yA)
        boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
        boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
        iou = interArea / float(boxAArea + boxBArea - interArea + 1e-5)
        return iou

    def match_bboxes(self, detections):
        assigned_ids = {}
        old_ids = list(self.tracked_movers.keys())
        old_bboxes = list(self.tracked_movers.values())

        if not old_bboxes:
            for det in detections:
                assigned_ids[self.next_id] = det
                self.tracked_movers[self.next_id] = det
                self.next_id += 1
            return assigned_ids

        cost_matrix = np.zeros((len(old_bboxes), len(detections)))
        for i, old_box in enumerate(old_bboxes):
            for j, new_box in enumerate(detections):
                cost_matrix[i, j] = 1 - self.iou(old_box, new_box)

        row_ind, col_ind = linear_sum_assignment(cost_matrix)

        matched_old = set()
        matched_new = set()

        for r, c in zip(row_ind, col_ind):
            if cost_matrix[r][c] < (1 - 0.3):  # IOU > 0.3
                mover_id = old_ids[r]
                assigned_ids[mover_id] = detections[c]
                self.tracked_movers[mover_id] = detections[c]
                matched_old.add(r)
                matched_new.add(c)

        for j, det in enumerate(detections):
            if j not in matched_new:
                assigned_ids[self.next_id] = det
                self.tracked_movers[self.next_id] = det
                self.next_id += 1

        return assigned_ids
