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
        self.new_variable = 42  # New variable example

    def new_function(self):  # New function example
        return "The meaning of life is: "

# -----------------------------------------------------------------------------------------------
# User-defined callback function
# -----------------------------------------------------------------------------------------------
def app_callback(pad, info, user_data):
    # Get the GstBuffer from the probe info
    buffer = info.get_buffer()
    if buffer is None:
        return Gst.PadProbeReturn.OK

    # Increment the frame count
    user_data.increment()

    # Get the caps from the pad
    format, width, height = get_caps_from_pad(pad)

    # If the user_data.use_frame is set to True, we can get the video frame from the buffer
    frame = None
    if user_data.use_frame and format is not None and width is not None and height is not None:
        # Get video frame
        frame = get_numpy_from_buffer(buffer, format, width, height)

    # Get the detections from the buffer
    roi = hailo.get_roi_from_buffer(buffer)
    detections = roi.get_objects_typed(hailo.HAILO_DETECTION)

    # Count the number of filters detected
    filter_count = 0
    for detection in detections:
        label = detection.get_label()
        if label == "filtre":  # Only count "filtre" labels
            filter_count += 1

    # Overlay the filter count on the video frame
    if user_data.use_frame and frame is not None:
        # Add filter count in red text
        cv2.putText(
            frame,
            f"Filters detected: {filter_count}",
            (50, 50),  # Position on the frame
            cv2.FONT_HERSHEY_SIMPLEX,
            2,  # Font size
            (0, 0, 255),  # Color (red)
            4,  # Thickness
        )

        # Convert the frame to BGR for OpenCV
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        cv2.imshow("Detection Output", frame)

    cv2.waitKey(1)  # Necessary for OpenCV to display the frame
    return Gst.PadProbeReturn.OK

# -----------------------------------------------------------------------------------------------
# Main function
# -----------------------------------------------------------------------------------------------
if __name__ == "__main__":
    # Initialize GStreamer
    Gst.init(None)

    # Create an instance of the user app callback class
    user_data = user_app_callback_class()
    user_data.use_frame = True  # Ensure this is True to enable frame processing

    # Start the GStreamer pipeline
    app = GStreamerDetectionApp(app_callback, user_data)
    app.run()
