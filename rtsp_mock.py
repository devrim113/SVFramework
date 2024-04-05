import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GLib
from config import STREAMING_PORT, STREAMING_PATH, STREAMING_URL
import signal
import sys
import simulation

def stop_server(sig, frame):
    print("\nStopping RTSP server")
    loop.quit()
    server = None
    print("Server stopped successfully.")
    sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        simulation_type = sys.argv[1]
    else:
        print("Please specify a simulation to run.")
        sys.exit(1)

    # Initialize GStreamer
    Gst.init(None)

    # Create an RTSP server
    server = GstRtspServer.RTSPServer.new()
    server.set_service(STREAMING_PORT)

    # Create a default media factory that will create a pipeline for a URI.
    factory = GstRtspServer.RTSPMediaFactory.new()
    if simulation_type == "low_bitrate":
        launch_string = simulation.low_bitrate()
    else:
        test = simulation.low_bitrate()
        print(test)
        launch_string = "( filesrc location=./input.mp4 ! qtdemux ! queue ! h264parse ! rtph264pay name=pay0 pt=96 )"
    factory.set_launch(launch_string)
    factory.set_shared(True)  # Share the pipeline between all clients

    # Attach the factory to the defined streaming path
    mounts = server.get_mount_points()
    mounts.add_factory(STREAMING_PATH, factory)

    # Start the server
    server.attach(None)

    # Run the GMainLoop to handle clients
    loop = GLib.MainLoop.new(None, False)

    # Handle SIGINT for stopping the server
    signal.signal(signal.SIGINT, stop_server)

    print("RTSP server is running on " + STREAMING_URL)
    loop.run()
