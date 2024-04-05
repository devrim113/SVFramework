import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GLib

# Initialize GStreamer
Gst.init(None)

# Create an RTSP server
server = GstRtspServer.RTSPServer.new()
server.set_service("8554")  # Set the port you want to listen on

# Create a default media factory that will create a pipeline for a URI.
factory = GstRtspServer.RTSPMediaFactory.new()
factory.set_launch("( filesrc location=./input.mp4 ! qtdemux ! queue ! h264parse ! rtph264pay name=pay0 pt=96 )")
factory.set_shared(True)  # Share the pipeline between all clients

# Attach the test factory to the /test endpoint
mounts = server.get_mount_points()
mounts.add_factory("/", factory)

# Start the server
server.attach(None)

# Run the GMainLoop to handle clients
loop = GLib.MainLoop.new(None, False)
loop.run()
