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


def network_congestion(video_file, rate="1mbit", latency="50ms"):
    """
    Simulate network congestion on the network interface by limiting the bandwidth using TBF along with netem for delay.
    Args:
        video_file: The video file to stream.
        rate: The maximum rate of traffic (e.g., '1mbit' for 1 Mbps).
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


# ------------------------- OCR Simulations -------------------------


def low_resolution(video_file, scale_factor=0.2):
    """
    Simulate a low resolution video by downscaling the input video.
    Args:
        video_file: The video file to process.
        scale_factor (float): The factor to scale the video by.
    Returns:
        str: The GStreamer launch string for the low resolution simulation.
    """
    output_video = (
        video_file.rsplit(".", 1)[0]
        + "_temp_low_resolution."
        + video_file.rsplit(".", 1)[1]
    )
    command = [
        "ffmpeg",
        "-i",
        video_file,
        "-vf",
        f"scale=iw*{scale_factor}:-1",
        output_video,
    ]
    subprocess.run(command)
    print(f"Created video file with low resolution: {output_video}")
    return normal(output_video)


def compression_artifacts(video_file, quality=50):
    """
    Simulate compression artifacts in a video by re-encoding it with a lower quality setting.
    Args:
        video_file: The video file to process.
        quality (int): The quality setting for the re-encoding (0-51 with 0 being lossless and 51 being the worst).
    Returns:
        str: The GStreamer launch string for the compression artifacts simulation.
    """
    output_video = (
        video_file.rsplit(".", 1)[0]
        + "_temp_compression_artifacts."
        + video_file.rsplit(".", 1)[1]
    )
    command = ["ffmpeg", "-i", video_file, "-crf", str(quality), output_video]
    subprocess.run(command)
    print(f"Created video file with compression artifacts: {output_video}")
    return normal(output_video)


def change_brightness(video_file, brightness_factor=0.5):
    """
    Adjust the brightness of a video by applying a brightness filter with FFmpeg.
    Args:
        video_file (str): The video file to process.
        brightness_factor (float): The brightness adjustment factor (-1.0 to 1.0,
                                   where negative values decrease and positive values increase brightness).
    Returns:
        str: The GStreamer launch string for the brightness adjustment simulation.
    """
    output_video = (
        video_file.rsplit(".", 1)[0]
        + "_temp_brightness."
        + video_file.rsplit(".", 1)[1]
    )
    command = [
        "ffmpeg",
        "-i",
        video_file,
        "-vf",
        f"eq=brightness={brightness_factor}",
        output_video,
    ]
    subprocess.run(command)
    print(f"Created video file with adjusted brightness: {output_video}")
    return normal(output_video)


def dynamic_change_brightness(video_file, brightness_factor=0.8, period=20):
    """
    Gradually adjust the brightness of a video from dark to bright and back to dark over the video duration.
    Args:
        video_file (str): The video file to process.
    Returns:
        str: The GStreamer launch string for the dynamic brightness adjustment simulation.
    """
    output_video = (
        video_file.rsplit(".", 1)[0]
        + "_temp_dynamic_brightness."
        + video_file.rsplit(".", 1)[1]
    )
    command = [
        "ffmpeg",
        "-i",
        video_file,
        "-vf",
        f"eq=brightness=sin(2*PI*t/{period})*{brightness_factor}:eval=frame",
        output_video,
    ]
    subprocess.run(command)
    print(f"Created video file with dynamic brightness adjustment: {output_video}")
    return normal(output_video)


def complex_blur(video_file, blur_factor=9):
    """
    Apply motion blur to simulate rapid movements or camera shake.
    Args:
        video_file (str): The video file to process.
        blur_factor (int): Defines the intensity of motion blur effect.
    Returns:
        str: The path to the motion blurred video.
    """
    output_video = (
        video_file.rsplit(".", 1)[0]
        + "_temp_complex_blur."
        + video_file.rsplit(".", 1)[1]
    )
    command = [
        "ffmpeg",
        "-hwaccel",
        "auto",
        "-i",
        video_file,
        "-vf",
        f"minterpolate='mi_mode=mci:mc_mode=aobmc:vsbmc=1',tblend='all_mode=average:all_opacity=0.{blur_factor}'",
        output_video,
    ]
    subprocess.run(command)
    print(f"Created video file with motion blur: {output_video}")
    return normal(output_video)


def simple_blur(video_file, blur_intensity=5):
    """
    Apply motion blur to simulate rapid movements or camera shake.
    Args:
        video_file (str): The video file to process.
        blur_intensity (int): Defines the intensity of the blur effect, higher values mean more blur.
    Returns:
        str: The path to the motion blurred video.
    """
    output_video = (
        video_file.rsplit(".", 1)[0]
        + "_temp_simple_blur."
        + video_file.rsplit(".", 1)[1]
    )
    command = [
        "ffmpeg",
        "-i",
        video_file,
        "-vf",
        f"avgblur={blur_intensity}",
        output_video,
    ]
    subprocess.run(command)
    print(f"Created video file with motion blur: {output_video}")
    return normal(output_video)


def change_contrast(video_file, contrast_factor=2.0):
    """
    Adjust the contrast levels of a video by applying a contrast filter with FFmpeg.
    Args:
        video_file (str): The video file to process.
        contrast_factor (float): The contrast adjustment factor, between -1000 and 1000.
    Returns:
        str: The path to the contrast-adjusted video.
    """
    output_video = (
        video_file.rsplit(".", 1)[0] + "_temp_contrast." + video_file.rsplit(".", 1)[1]
    )
    command = [
        "ffmpeg",
        "-i",
        video_file,
        "-vf",
        f"eq=contrast={contrast_factor}",
        output_video,
    ]
    subprocess.run(command)
    print(f"Created video file with adjusted contrast: {output_video}")
    return normal(output_video)


def dynamic_change_contrast(video_file, contrast_factor=900.0, period=20):
    """
    Dynamically adjust the contrast levels of a video over its duration.
    Args:
        video_file (str): The video file to process.
        contrast_factor (float): The factor by which to adjust the contrast, between -1000 and 1000.
        period (int): The period of contrast change cycle.
    Returns:
        str: The path to the contrast-adjusted video.
    """
    output_video = (
        video_file.rsplit(".", 1)[0]
        + "_temp_dynamic_contrast."
        + video_file.rsplit(".", 1)[1]
    )
    # Adjusting the formula to ensure smoother transition
    command = [
        "ffmpeg",
        "-i",
        video_file,
        "-vf",
        f"eq=contrast='sin(2*PI*t/{period})*{contrast_factor/1000} + 1':eval=frame",
        output_video,
    ]
    subprocess.run(command)
    print(f"Created video file with dynamic contrast adjustment: {output_video}")
    return normal(output_video)


def background_noise(video_file, noise_intensity=50):
    """
    Add background noise to simulate visual clutter.
    Args:
        video_file (str): The video file to process.
        noise_intensity (int): The intensity level of noise, scale of 0 to 100.
    Returns:
        str: The path to the noise-added video.
    """
    output_video = (
        video_file.rsplit(".", 1)[0] + "_temp_noise." + video_file.rsplit(".", 1)[1]
    )
    command = [
        "ffmpeg",
        "-i",
        video_file,
        "-vf",
        f"noise=alls={noise_intensity}:allf=t+u",
        output_video,
    ]
    subprocess.run(command)
    print(f"Created video file with background noise: {output_video}")
    return normal(output_video)
