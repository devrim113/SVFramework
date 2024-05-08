#! /usr/bin/env python3
"""
This is the main script for running simulations as RTSP servers.
The script takes a video folder and a simulation type as arguments and runs the specified simulation as an RTSP server.
A seperate RTSP server is created for each video file in the folder.
The available simulation types are defined in the simulations module.
Usage: python simulator.py <video_folder> <simulation_type>
"""

import subprocess
from config import NETWORK_INTERFACE, STREAMING_PORT, STREAMING_URL
import signal
import sys
import simulations
import gi

gi.require_version("Gst", "1.0")
gi.require_version("GstRtspServer", "1.0")
from gi.repository import Gst, GstRtspServer, GLib
import os


def run_simulation(videos, simulation_type, video_folder_path):
    """
    Run the specified simulation type as an RTSP server for each video file in the video folder.
    Args:
        videos: The folder containing the video files to stream.
        simulation_type: The type of simulation to run.
        video_folder_path: The path to the video folder.
    Returns:
        None
    Starts:
        RTSP server for each video file in the video folder.
    """
    # Check if the simulation type is valid
    if simulation_type not in simulation_types:
        print("Invalid simulation type. Please specify a valid simulation.")
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
    print(f"Running {simulation_type} simulation...")
    for video_file in videos:
        launch_string = getattr(simulations, simulation_type)(video_file)
        factory = GstRtspServer.RTSPMediaFactory.new()
        # Set the launch string for the media factory
        factory.set_launch(launch_string)
        # Share the pipeline between all clients
        factory.set_shared(True)

        # Attach the factory to the streaming path for the video file
        mounts = server.get_mount_points()
        mounts.add_factory("/" + os.path.basename(video_file), factory)

        # Print all the streams available
        print(f"Stream available at {STREAMING_URL}{os.path.basename(video_file)}")

    # Start the server
    server.attach(None)

    # Run the GMainLoop to handle clients
    loop = GLib.MainLoop.new(None, False)

    def handle_sigint(sig, frame):
        """
        Stop the RTSP server when a SIGINT signal is received.
        """
        print("\nStopping RTSP server...")
        loop.quit()
        print("Server stopped successfully.")
        remove_network_simulation()
        delete_temp_videos(video_folder_path)
        sys.exit(0)

    # Handle SIGINT for stopping the server
    signal.signal(signal.SIGINT, handle_sigint)

    print("Simulator is ready")
    loop.run()


def remove_network_simulation():
    """
    Remove the introduced tc configurations to simulate network conditions.
    Args:
        None
    Returns:
        None
    """
    print("\nStopping network simulation...")
    try:
        subprocess.run(
            ["sudo", "tc", "qdisc", "del", "dev", NETWORK_INTERFACE, "root"],
            check=True,
            stderr=subprocess.DEVNULL,
        )
        print("Network simulation stopped.")
    except subprocess.CalledProcessError:
        print("No network simulation active, continuing.")


def delete_temp_videos(video_folder_path):
    """
    Delete the temporary video files created during the simulations in the video folder.
    Delete all video files that end in '_temp' with any extension.
    Args:
        video_folder: The folder containing the video files to delete.
    Returns:
        None
    """
    print("\nDeleting temporary video files...")
    for video_file in os.listdir(video_folder_path):
        if "_temp" in video_file:
            full_path = os.path.join(video_folder_path, video_file)
            print(f"Deleting temporary video file {full_path}...")
            os.remove(full_path)
            print(f"Deleted {full_path} successfully.")
    else:
        print("No more temporary video files found, continuing.")


if __name__ == "__main__":
    # Get the available simulation types from the simulation module
    simulation_types = sorted(
        [
            func
            for func in dir(simulations)
            if callable(getattr(simulations, func)) and not func.startswith("__")
        ],
        key=lambda x: getattr(simulations, x).__code__.co_firstlineno,
    )

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
            and video.lower().endswith((".mp4", ".avi", ".mkv", ".ts"))
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
            print("Usage: python3 simulator.py <video_folder> <simulation_type>")
            print("Available simulations: " + ", ".join(simulation_types))
            sys.exit(1)
    else:
        print("Please specify a simulation and a video folder to run.")
        print("Usage: python3 simulator.py <video_folder> <simulation_type>")
        print("Available simulations: " + ", ".join(simulation_types))
        sys.exit(1)

    run_simulation(videos, simulation_type, video_folder)
