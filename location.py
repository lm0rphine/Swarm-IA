import cv2
import numpy as np
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
# Define Positions on the Frame
# -----------------------------------------------------------------------------------------------
def define_positions(frame):
    """
    Define 12 rectangular regions in the frame for the 12 filter positions.
    """
    height, width, _ = frame.shape

    # Example grid-based setup for simplicity (adjust coordinates as needed)
    positions = {
        1: (0, 0, width // 4, height // 3),    # Top-left
        2: (width // 4, 0, width // 2, height // 3),  # Top-center
        3: (width // 2, 0, 3 * width // 4, height // 3),  # Top-right
        4: (3 * width // 4, 0, width, height // 3),  # Top-right corner
        5: (0, height // 3, width // 4, 2 * height // 3),  # Middle-left
        6: (width // 4, height // 3, width // 2, 2 * height // 3),  # Middle-center
        7: (width // 2, height // 3, 3 * width // 4, 2 * height // 3),  # Middle-right
        8: (3 * width // 4, height // 3, width, 2 * height // 3),  # Middle-right corner
        9: (0, 2 * height // 3, width // 4, height),  # Bottom-left
        10: (width // 4, 2 * height // 3, width // 2, height),  # Bottom-center
        11: (width // 2, 2 * height // 3, 3 * width // 4, height),  # Bottom-right
        12: (3 * width // 4, 2 * height // 3, width, height),  # Bottom-right corner
    }

    return positions


# -----------------------------------------------------------------------------------------------
# User-defined callback function
# -----------------------------------------------------------------------------------------------
def app_callback(pad, info, user_data):
    # Get the GstBuffer from the probe info
    buffer = info.get_buffer()
    if buffer is None:
        return Gst.PadProbeReturn.OK

    # Get the caps from the pad
    format, width, height = get_caps_from_pad(pad)

    # Get video frame
    frame = None
    if user_data.use_frame and format is not None and width is not None and height is not None:
        frame = get_numpy_from_buffer(buffer, format, width, height)

    # Define filter positions
    positions = define_positions(frame)

    # Get the detections from the buffer
    roi = hailo.get_roi_from_buffer(buffer)
    detections = roi.get_objects_typed(hailo.HAILO_DETECTION)

    # Check filter positions
    for detection in detections:
        label = detection.get_label()
        if label == "filtre":  # Only consider "filtre" detections
            bbox = detection.get_bbox()  # Bounding box (x_min, y_min, x_max, y_max)
            x_center = (bbox[0] + bbox[2]) // 2
            y_center = (bbox[1] + bbox[3]) // 2

            # Determine which position the center falls into
            for position, (x_min, y_min, x_max, y_max) in positions.items():
                if x_min <= x_center <= x_max and y_min <= y_center <= y_max:
                    print(f"Position {position} occupied")
                    cv2.putText(
                        frame,
                        f"Position {position} occupied",
                        (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 0, 255),
                        2,
                    )

    # Display the frame with overlays
    for position, (x_min, y_min, x_max, y_max) in positions.items():
        cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (255, 255, 0), 2)  # Draw positions
    cv2.imshow("Detection Output", frame)
    cv2.waitKey(1)

    return Gst.PadProbeReturn.OK


# -----------------------------------------------------------------------------------------------
# Main function
# -----------------------------------------------------------------------------------------------
if __name__ == "__main__":
    # Create an instance of the user app callback class
    user_data = user_app_callback_class()
    user_data.use_frame = True  # Ensure this is True to enable frame processing

    # Start the GStreamer pipeline
    app = GStreamerDetectionApp(app_callback, user_data)
    app.run()
