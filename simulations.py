#! /usr/bin/env python3
"""
This is the simulations module for defining different simulation types for the RTSP server.
It should not be run, but imported by the simulator script.
"""

import subprocess
from config import NETWORK_INTERFACE

streams_simulated = 0

# ------------------------- Gstreamer Simulations -------------------------


def normal(video_file):
    """
    Simulate a normal video stream with default encoding settings.
    Args:
        video_file: The video file to stream.
    Returns:
        str: The GStreamer launch string for the normal simulation.
    """
    return f"( filesrc location=./{video_file} ! decodebin ! x264enc ! rtph264pay name=pay0 pt=96 )"


def low_bitrate(video_file):
    """
    Simulate a video stream with low bitrate encoding settings.
    Args:
        video_file: The video file to stream.
    Returns:
        str: The GStreamer launch string for the low bitrate simulation.
    """
    return f"( filesrc location=./{video_file} ! decodebin ! x264enc bitrate=50 ! rtph264pay name=pay0 pt=96 )"


# ------------------------- Network Simulations -------------------------


def increased_latency(video_file, delay="100ms", jitter="10ms"):
    """
    Simulate a video stream with increased latency to test the system's ability to handle delays.
    Applies a fixed delay to every packet.
    Args:
        video_file: The video file to stream.
        delay: The delay to introduce in the stream.
        jitter: The jitter to introduce in the stream.
    Returns:
        str: The GStreamer launch string for the increased latency simulation.
    """
    # Replace the existing network interface settings with increased latency
    subprocess.run(
        [
            "sudo",
            "tc",
            "qdisc",
            "replace",
            "dev",
            NETWORK_INTERFACE,
            "root",
            "netem",
            "delay",
            delay,
            jitter,
        ],
        check=True,
    )
    # Return a normal simulation string as the network simulation is now active
    return normal(video_file)


def packet_loss(video_file, loss_rate="10%"):
    """
    Simulate a video stream with packet loss to test the system's ability to handle network errors.
    Args:
        video_file: The video file to stream.
    Returns:
        str: The GStreamer launch string for the packet loss simulation.
    """
    # Replace the exisiting network interface settings with packet loss
    subprocess.run(
        [
            "sudo",
            "tc",
            "qdisc",
            "replace",
            "dev",
            NETWORK_INTERFACE,
            "root",
            "netem",
            "loss",
            loss_rate,
        ],
        check=True,
    )
    # Return a normal simulation string as the network simulation is now active
    return normal(video_file)


def limited_bandwidth(video_file, rate="1mbit"):
    """
    Simulate a video stream with limited bandwidth.
    Args:
        video_file: The video file to stream.
        rate: The maximum rate of traffic.
    Returns:
        str: The GStreamer launch string for the bandwidth limitation simulation.
    """
    # Replace the existing network interface settings with limited bandwidth
    subprocess.run(
        [
            "sudo",
            "tc",
            "qdisc",
            "replace",
            "dev",
            NETWORK_INTERFACE,
            "root",
            "tbf",
            "rate",
            rate,
            "burst",
            "32kbit",
            "latency",
            "400ms",
        ],
        check=True,
    )
    # Return a normal simulation string as the network simulation is now active
    return normal(video_file)


def jitter(video_file, delay="100ms", jitter="50ms"):
    """
    Simulate a video stream with jitter in network latency.
    Introduces variability in the delay of packets.
    Args:
        video_file: The video file to stream.
        delay: The base delay to add to packets.
        jitter: The random variation in delay.
    Returns:
        str: The GStreamer launch string for the jitter simulation.
    """
    # Replace the existing network interface settings with jitter
    subprocess.run(
        [
            "sudo",
            "tc",
            "qdisc",
            "replace",
            "dev",
            NETWORK_INTERFACE,
            "root",
            "netem",
            "delay",
            delay,
            jitter,
            "distribution",
            "normal",
        ],
        check=True,
    )
    # Return a normal simulation string as the network simulation is now active
    return normal(video_file)


def packet_duplication(video_file, duplication_rate="10%"):
    """
    Simulate packet duplication on the network interface.
    Args:
        video_file: The video file to stream.
        duplication_rate: Percentage of packets to duplicate.
    Returns:
        str: The GStreamer launch string for the packet duplication simulation.
    """
    # Replace the existing network interface settings with packet duplication
    subprocess.run(
        [
            "sudo",
            "tc",
            "qdisc",
            "replace",
            "dev",
            NETWORK_INTERFACE,
            "root",
            "netem",
            "duplicate",
            duplication_rate,
        ],
        check=True,
    )
    # Return a normal simulation string as the network simulation is now active
    return normal(video_file)


def packet_reordering(video_file, correlation="25%", delay="50ms"):
    """
    Simulate packet reordering on the network interface.
    Args:
        video_file: The video file to stream.
        correlation: Percentage describing how much reordering should be correlated.
        delay: Additional delay to apply to help ensure reordering occurs.
    Returns:
        str: The GStreamer launch string for the packet reordering simulation.
    """
    # Replace the existing network interface settings with packet reordering
    subprocess.run(
        [
            "sudo",
            "tc",
            "qdisc",
            "replace",
            "dev",
            NETWORK_INTERFACE,
            "root",
            "netem",
            "delay",
            delay,
            "reorder",
            correlation,
        ],
        check=True,
    )
    # Return a normal simulation string as the network simulation is now active
    return normal(video_file)


def packet_corruption(video_file, corruption_rate="0.1%"):
    """
    Simulate packet corruption on the network interface.
    Args:
        video_file: The video file to stream.
        corruption_rate: Percentage of packets that should be corrupted.
    Returns:
        str: The GStreamer launch string for the packet corruption simulation.
    """
    # Replace the existing network interface settings with packet corruption
    subprocess.run(
        [
            "sudo",
            "tc",
            "qdisc",
            "replace",
            "dev",
            NETWORK_INTERFACE,
            "root",
            "netem",
            "corrupt",
            corruption_rate,
        ],
        check=True,
    )
    # Return a normal simulation string as the network simulation is now active
    return normal(video_file)


def network_congestion(video_file, rate="1mbit", burst="10kb", latency="50ms"):
    """
    Simulate network congestion on the network interface by limiting the bandwidth using TBF along with netem for delay.
    Args:
        video_file: The video file to stream.
        rate: The maximum rate of traffic (e.g., '1mbit' for 1 Mbps).
        burst: The maximum burst size allowed (controls burstiness).
        latency: Simulate additional delay to represent network congestion effects.
    Returns:
        str: The GStreamer launch string for the network congestion simulation.
    """

    subprocess.run(
        [
            "sudo",
            "tc",
            "qdisc",
            "replace",
            "dev",
            NETWORK_INTERFACE,
            "root",
            "handle",
            "1:",
            "netem",
            "rate",
            rate,
            "delay",
            latency,
            "loss",
            "0.1%",
            "duplicate",
            "0.1%",
        ],
        check=True,
    )
    # Return a normal simulation string as the network simulation is now active
    return normal(video_file)


# ------------------------- Camera Simulations -------------------------


def audio_sync(video_file, audio_delay_ms="500"):
    """
    Simulate synchronization issues between audio and video by introducing a delay in the audio stream.
    Args:
        video_file: The video file to stream.
        audio_delay_ms: The amount of delay to introduce to the audio stream, in milliseconds.
    Returns:
        str: The GStreamer launch string for the audio-video synchronization issue simulation.
    """
    return (
        f"( filesrc location=./{video_file} ! decodebin name=dec "
        f"dec. ! queue ! audioconvert ! audioresample !"
        f"queue min-threshold-time={audio_delay_ms}000000 ! avenc_aac ! queue ! mux. "
        f"dec. ! videoconvert ! videoscale ! x264enc bitrate=500 ! queue ! mux. "
        f"matroskamux name=mux ! rtph264pay name=pay0 pt=96 )"
    )


# ------------------------- Array Camera Simulations -------------------------


def hardware_failure(video_file):
    """
    Simulate a hardware failure in an array camera by streaming a video
    that provides no actual video content (e.g., a black screen).
    Args:
        video_file: The video file to stream. Not used in this simulation, but kept for consistency.
    Returns:
        str: The GStreamer launch string for the hardware failure simulation.
    """
    global streams_simulated
    streams_simulated += 1
    # Every fourth stream will be a black screen
    if streams_simulated % 4 == 0:
        return "( videotestsrc pattern=black ! video/x-raw,width=1920,height=1080,framerate=24/1 \
                ! x264enc bitrate=500 ! rtph264pay name=pay0 pt=96 )"
    else:
        return normal(video_file)


def camera_delay(video_file):
    """
    Simulate one of the cameras in an array camera system having a delay in its video stream.
    Args:
        video_file: The video file to stream.
    Returns:
        str: The GStreamer launch string for the camera delay simulation.
    """
    global streams_simulated
    streams_simulated += 1
    # Every fourth stream will have a delay
    if streams_simulated % 4 == 0:
        return (
            f"( filesrc location=./{video_file} ! decodebin ! queue min-threshold-time=10000000000000000 ! "
            f"x264enc bitrate=500 ! rtph264pay name=pay0 pt=96 )"
        )
    else:
        return normal(video_file)
