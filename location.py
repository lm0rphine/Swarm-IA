import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
import os
import numpy as np
import cv2
import hailo
from hailo_rpi_common import (
    get_caps_from_pad,
    get_numpy_from_buffer,
    app_callback_class,
)
from detection_pipeline import GStreamerDetectionApp

# -----------------------------------------------------------------------------------------------
# User-defined class to be used in the callback function
# -----------------------------------------------------------------------------------------------
class user_app_callback_class(app_callback_class):
    def __init__(self):
        super().__init__()

# -----------------------------------------------------------------------------------------------
# Define Regions with Provided Coordinates
# -----------------------------------------------------------------------------------------------
def define_regions(frame_width, frame_height):
    """
    Define custom regions manually based on provided coordinates.
    The coordinates are normalized to the frame dimensions if necessary.
    """
    regions = {
        1: (414, 98, 656, 307),
        2: (775, 93, 1028, 321),
        3: (1150, 101, 1396, 332),
        4: (1515, 117, 1768, 339),
        5: (385, 452, 644, 689),
        6: (759, 450, 1019, 695),
        7: (1155, 454, 1423, 703),
        8: (1533, 461, 1771, 705),
        9: (352, 843, 617, 1080),
        10: (760, 841, 1025, 1090),
        11: (1141, 839, 1405, 1087),
        12: (1536, 833, 1788, 1089),
    }
    return regions

# -----------------------------------------------------------------------------------------------
# User-defined callback function
# -----------------------------------------------------------------------------------------------
def app_callback(pad, info, user_data):
    # Get the GstBuffer from the probe info
    buffer = info.get_buffer()
    if buffer is None:
        return Gst.PadProbeReturn.OK

    # Using the user_data to count the number of frames
    user_data.increment()

    # Get the caps from the pad
    format, width, height = get_caps_from_pad(pad)

    # If the user_data.use_frame is set to True, we can get the video frame from the buffer
    frame = None
    if user_data.use_frame and format is not None and width is not None and height is not None:
        # Get video frame
        frame = get_numpy_from_buffer(buffer, format, width, height)

    # Define the 12 regions based on provided coordinates
    regions = define_regions(width, height)

    # Get the detections from the buffer
    roi = hailo.get_roi_from_buffer(buffer)
    detections = roi.get_objects_typed(hailo.HAILO_DETECTION)

    # Check detected objects and their positions
    for detection in detections:
        label = detection.get_label()
        if label == "filtre":  # Only check "filtre" labels
            bbox = detection.get_bbox()

            # Get the bounding box coordinates in pixels
            x_min = int(bbox.xmin() * width)
            y_min = int(bbox.ymin() * height)
            x_max = int(bbox.xmax() * width)
            y_max = int(bbox.ymax() * height)

            # Calculate the center point of the detection
            x_center = (x_min + x_max) // 2
            y_center = (y_min + y_max) // 2

            # Determine which region the center point falls into
            for region_num, (rx_min, ry_min, rx_max, ry_max) in regions.items():
                if rx_min <= x_center <= rx_max and ry_min <= y_center <= ry_max:
                    print(f"Position {region_num} occupied by Filtre")
                    break  # No need to check other regions once matched

    # Draw the regions on the frame for visualization
    if user_data.use_frame and frame is not None:
        for region_num, (rx_min, ry_min, rx_max, ry_max) in regions.items():
            # Draw region boundaries
            cv2.rectangle(frame, (rx_min, ry_min), (rx_max, ry_max), (255, 0, 0), 2)
            # Label the regions
            cv2.putText(
                frame,
                f"{region_num}",
                (rx_min + 10, ry_min + 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
            )
        # Display the frame
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        cv2.imshow("Detection Output", frame_bgr)
        cv2.waitKey(1)

    return Gst.PadProbeReturn.OK

# -----------------------------------------------------------------------------------------------
# Main function
# -----------------------------------------------------------------------------------------------
if __name__ == "__main__":
    # Create an instance of the user app callback class
    user_data = user_app_callback_class()
    user_data.use_frame = True  # Ensure this is True to enable frame processing
    app = GStreamerDetectionApp(app_callback, user_data)
    app.run()
