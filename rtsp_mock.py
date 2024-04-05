import subprocess
import os

def start_gstreamer_rtsp_server(video_path):
    # Define the GStreamer pipeline with looping
    pipeline = (
        f"multifilesrc location={video_path} loop=true ! "  # Set loop=true for looping
        f"qtdemux ! h264parse ! rtph264pay name=pay0 pt=96 config-interval=1 ! "
        f"gdppay ! tcpserversink host=localhost port=8554"
    )

    # Run the GStreamer command
    subprocess.Popen(["gst-launch-1.0", "-v"] + pipeline.split())

# Example usage
video_path = os.path.join(os.path.dirname(__file__), "input.mp4")
start_gstreamer_rtsp_server(video_path)
