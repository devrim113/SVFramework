import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GLib
from config import STREAMING_PORT, STREAMING_PATH, STREAMING_URL
import signal

# Initialize GStreamer
Gst.init(None)

# Create an RTSP server
server = GstRtspServer.RTSPServer.new()
server.set_service(STREAMING_PORT)  # Set the port you want to listen on

# Create a default media factory that will create a pipeline for a URI.
factory = GstRtspServer.RTSPMediaFactory.new()
factory.set_launch("( filesrc location=./input.mp4 ! qtdemux ! queue ! h264parse ! rtph264pay name=pay0 pt=96 )")
factory.set_shared(True)  # Share the pipeline between all clients

# Attach the test factory to the /test endpoint
mounts = server.get_mount_points()
mounts.add_factory(STREAMING_PATH, factory)

# Start the server
server.attach(None)

# Run the GMainLoop to handle clients
loop = GLib.MainLoop.new(None, False)

def stop_server(sig, frame):
    print("\nStopping RTSP server")
    loop.quit()
    server = None
    print("Server stopped successfully.")
    exit(0)

# Handle SIGINT for stopping the server
signal.signal(signal.SIGINT, stop_server)

print("RTSP server is running on " + STREAMING_URL)
loop.run()