from config import STREAMING_PORT, STREAMING_PATH, STREAMING_URL
import signal
import sys
import simulations
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GLib


def stop_server(sig, frame):
    print("\nStopping RTSP server")
    loop.quit()
    print("Server stopped successfully.")
    sys.exit(0)


if __name__ == "__main__":
    # Get the available simulation types from the simulation module
    simulation_types = [func for func in dir(simulations) if callable(getattr(simulations, func)) and not func.startswith("__")]

    # Get the simulation type from the command line arguments
    if len(sys.argv) > 1:
        simulation_type = sys.argv[1]
    else:
        print("Please specify a simulation to run.")
        print("Available simulations: " + ", ".join(simulation_types))
        sys.exit(1)

    # Initialize GStreamer
    Gst.init(None)

    # Create an RTSP server
    server = GstRtspServer.RTSPServer.new()
    server.set_service(STREAMING_PORT)

    # Create a default media factory that will create a pipeline for a URI.
    factory = GstRtspServer.RTSPMediaFactory.new()

    # Perform the operations for the specified simulation type
    if simulation_type in simulation_types:
        launch_string = getattr(simulations, simulation_type)()
    else:
        print("Invalid simulation type. Please specify a valid simulation.")
        print("Available simulations: " + ", ".join(simulation_types))
        sys.exit(1)

    # Set the launch string for the media factory
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
