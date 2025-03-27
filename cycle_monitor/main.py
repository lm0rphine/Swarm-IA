# main.py

from hailo_apps_infra.detection_pipeline import GStreamerDetectionApp
from pipeline.detection_app import app_callback, user_app_callback_class

if __name__ == "__main__":
    user_data = user_app_callback_class()
    app = GStreamerDetectionApp(app_callback, user_data)
    app.run()
