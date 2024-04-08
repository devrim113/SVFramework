#! /usr/bin/env python3
"""
This is the main script for running simulations as RTSP servers.
The script takes a video folder and a simulation type as arguments and runs the specified simulation as an RTSP server.
A seperate RTSP server is created for each video file in the folder.
The available simulation types are defined in the simulations module.
Usage: python simulator.py <video_folder> <simulation_type>
"""

from config import STREAMING_PORT, STREAMING_URL
import signal
import sys
import simulations
import gi

gi.require_version("Gst", "1.0")
gi.require_version("GstRtspServer", "1.0")
from gi.repository import Gst, GstRtspServer, GLib
import os


def run_simulation(video_folder, simulation_type):
    """
    Run the specified simulation type as an RTSP server for each video file in the video folder.
    Args:
        video_folder: The folder containing the video files to stream.
        simulation_type: The type of simulation to run.
    Returns:
        None
    Starts:
        RTSP server for each video file in the video folder.
    """

    # Initialize GStreamer
    Gst.init(None)

    # Create an RTSP server
    server = GstRtspServer.RTSPServer.new()
    server.set_service(STREAMING_PORT)

    # Create a default media factory that will create a pipeline for a URI.
    factory = GstRtspServer.RTSPMediaFactory.new()

    # Perform the operations for the specified simulation type
    if simulation_type in simulation_types:
        print(f"Running {simulation_type} simulation...")
        for video_file in video_folder:
            launch_string = getattr(simulations, simulation_type)(video_file)
            # Set the launch string for the media factory
            factory.set_launch(launch_string)
            # Share the pipeline between all clients
            factory.set_shared(True)

            # Attach the factory to the streaming path for the video file
            mounts = server.get_mount_points()
            mounts.add_factory("/" + os.path.basename(video_file), factory)

            # Print all the streams available
            print(f"Stream available at {STREAMING_URL}{os.path.basename(video_file)}")

    else:
        print("Invalid simulation type. Please specify a valid simulation.")
        print("Available simulations: " + ", ".join(simulation_types))
        sys.exit(1)

    # Start the server
    server.attach(None)

    # Run the GMainLoop to handle clients
    loop = GLib.MainLoop.new(None, False)

    def handle_sigint(sig, frame):
        """
        Stop the RTSP server when a SIGINT signal is received.
        """
        print("\nStopping RTSP server")
        loop.quit()
        print("Server stopped successfully.")
        sys.exit(0)

    # Handle SIGINT for stopping the server
    signal.signal(signal.SIGINT, handle_sigint)

    loop.run()


if __name__ == "__main__":
    # Get the available simulation types from the simulation module
    simulation_types = [
        func
        for func in dir(simulations)
        if callable(getattr(simulations, func)) and not func.startswith("__")
    ]

    # Get the simulation type from the command line arguments
    if len(sys.argv) > 2:
        video_folder = sys.argv[1]

        # Check if the video_folder exists, else throw an error.
        if not os.path.exists(video_folder):
            print(f"The video folder '{video_folder}' does not exist.")
            sys.exit(1)

        # Only append video files to the list of videos, files with extensions .mp4, .avi, .mkv.
        videos = [
            os.path.join(video_folder, video)
            for video in os.listdir(video_folder)
            if os.path.isfile(os.path.join(video_folder, video))
            and video.lower().endswith((".mp4", ".avi", ".mkv"))
        ]

        # Check if the video folder contains any video files
        if not videos:
            print(
                f"The video folder '{video_folder}' does not contain any video files."
            )
            sys.exit(1)

        # Check if the video files are accessible
        for video in videos:
            try:
                open(video)
            except FileNotFoundError:
                print(f"The video '{video}' is inaccessible.")
                sys.exit(1)

        simulation_type = sys.argv[2]

        # Check if the simulation type is valid
        if simulation_type not in simulation_types:
            print("Invalid simulation type. Please specify a valid simulation.")
            print("Usage: python simulator.py <video_folder> <simulation_type>")
            print("Available simulations: " + ", ".join(simulation_types))
            sys.exit(1)
    else:
        print("Please specify a simulation and a video folder to run.")
        print("Usage: python simulator.py <video_folder> <simulation_type>")
        print("Available simulations: " + ", ".join(simulation_types))
        sys.exit(1)

    run_simulation(videos, simulation_type)
