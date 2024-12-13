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
# Define 12 Regions on the Frame
# -----------------------------------------------------------------------------------------------
def define_regions(frame_width, frame_height):
    """
    Divide the frame into 12 equal regions (4 columns x 3 rows).
    Returns a dictionary mapping region numbers to bounding box coordinates.
    """
    regions = {}
    cols = 4  # Divide width into 4 columns
    rows = 3  # Divide height into 3 rows
    col_width = frame_width // cols
    row_height = frame_height // rows

    region_num = 1
    for row in range(rows):
        for col in range(cols):
            x_min = col * col_width
            y_min = row * row_height
            x_max = x_min + col_width
            y_max = y_min + row_height
            regions[region_num] = (x_min, y_min, x_max, y_max)
            region_num += 1

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

    # Define the 12 regions based on the frame dimensions
    regions = define_regions(width, height)

    # Get the detections from the buffer
    roi = hailo.get_roi_from_buffer(buffer)
    detections = roi.get_objects_typed(hailo.HAILO_DETECTION)

    # Check detected objects and their positions
    for detection in detections:
        label = detection.get_label()
        if label == "filtre":  # Only check "filtre" labels
            bbox = detection.get_bbox()
            x_center = (bbox[0] + bbox[2]) // 2
            y_center = (bbox[1] + bbox[3]) // 2

            # Determine which region the center point falls into
            for region_num, (x_min, y_min, x_max, y_max) in regions.items():
                if x_min <= x_center <= x_max and y_min <= y_center <= y_max:
                    print(f"Position {region_num} occupied by Filtre")

    # Draw the regions on the frame for visualization
    if user_data.use_frame and frame is not None:
        for region_num, (x_min, y_min, x_max, y_max) in regions.items():
            # Draw region boundaries
            cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (255, 0, 0), 2)
            # Label the regions
            cv2.putText(
                frame,
                f"{region_num}",
                (x_min + 10, y_min + 30),
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
