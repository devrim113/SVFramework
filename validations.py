#! /usr/bin/env python3
"""
This is the validations module for defining different validation types for the input data.
It should not be run, but imported by the validator script.
"""

import subprocess
import re
import time


def stream_running(url):
    """
    Check if the RTSP stream is accessible using ffprobe.
    Args:
        url: The URL of the RTSP stream to validate.
    Returns:
        bool: True if the stream is accessible, False otherwise.
    """
    print("Running and accessible...\t", end="")
    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=filename",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        url,
    ]
    result = subprocess.run(command, text=True, capture_output=True)

    # Stream is accessible if ffprobe exits with code 0
    if result.returncode == 0:
        print("Success! Stream is running and accessible.")
        return True
    return False


def minimum_fps(url, fps=20, duration=10):
    """
    Check if the actual FPS of the RTSP stream is at least the specified value over a given duration.
    Args:
        url: The URL of the RTSP stream.
        fps: The minimum frames per second expected.
        duration: The duration in seconds over which to measure the FPS.
    Returns:
        bool: True if the stream FPS meets or exceeds the specified value, False otherwise.
    """
    print(f"Minimum FPS of {fps}...\t", end="")
    command = [
        "ffmpeg",
        "-i",
        url,
        "-vcodec",
        "copy",
        "-an",
        "-t",
        str(duration),
        "-f",
        "null",
        "-",
    ]

    try:
        # Execute the command and capture the output
        result = subprocess.run(command, text=True, stderr=subprocess.PIPE)

        # Parse the output to find the number of frames processed
        output_lines = result.stderr.split("\n")
        frame_lines = [line for line in output_lines if "frame=" in line]
        if frame_lines:
            # Last occurrence of 'frame=' will have the count at the end of processing
            last_line = frame_lines[-1]
            frame_count = int(last_line.split("frame=")[1].split()[0])
            # Calculate actual FPS
            actual_fps = frame_count / duration
            print(f"Success! Measured FPS: {actual_fps} >= {fps}")
            return actual_fps >= fps
        else:
            print("No frame information found in ffmpeg output.")
            return False
    except Exception as e:
        print(f"Error measuring FPS with ffmpeg: {e}")
        return False


def minimum_resolution(url, min_width=640, min_height=480, duration=10):
    """
    Monitor the resolution of a live RTSP stream in real-time and checks if it meets a minimum resolution for a given duration.
    Args:
        url (str): URL of the RTSP stream.
        duration (int): Duration in seconds to monitor the stream.
        min_width (int): Minimum width in pixels.
        min_height (int): Minimum height in pixels.
    """
    print(f"Minimum resolution of {min_width}x{min_height}...\t", end="")
    # Command to decode the stream and extract frame resolution in real-time
    cmd = [
        'ffmpeg',
        '-i', url,
        '-vf', 'showinfo',  # Use showinfo filter to get information about each frame
        '-an',  # Disable audio processing to focus on video
        '-t', str(duration),  # Limit the processing to the specified duration
        '-f', 'null',  # Output to null since we only care about the logs
        '-'  # Output to stdout for parsing
    ]

    # Start the ffmpeg process
    process = subprocess.Popen(cmd, stderr=subprocess.PIPE, text=True)

    start_time = time.time()
    resolution_met = True  # Assume resolution is met unless proven otherwise

    try:
        for line in process.stderr:
            # Use a regex to find lines that contain resolution information
            if 'showinfo' in line:
                match = re.search(r'([0-9]+)x([0-9]+)\s', line)
                if match:
                    width, height = map(int, match.groups())
                    if width < min_width or height < min_height:
                        resolution_met = False
                        print(f"Resolution below minimum at {width}x{height}, required {min_width}x{min_height}")
                        break

        # Check if the minimum resolution was maintained throughout the duration
        if resolution_met and (time.time() - start_time >= duration):
            print(f"Measured Resolution: {width}x{height} >= {min_width}x{min_height} for {duration} seconds.")
            return True
        return False
    except Exception as e:
        print(f"Error processing ffmpeg output: {e}")
        return False


# def monitor_av_sync(url):
#     """
#     Monitors the audio-video synchronization of an RTSP stream in real-time using FFmpeg.
#     Args:
#         url: The URL of the RTSP stream from GStreamer.
#     Retruns:
#         None
#     """
#     cmd = [
#         'ffmpeg',
#         '-i', url,
#         '-map', '0:v:0',  # Select the first video stream
#         '-map', '0:a:0',  # Select the first audio stream
#         '-vcodec', 'copy',  # Copy the video codec
#         '-acodec', 'copy',  # Copy the audio codec
#         '-f', 'null',  # Output to null since we only care about the logs
#         '-'  # Output to stdout for parsing
#     ]

#     # Start the ffmpeg process
#     process = subprocess.Popen(cmd, stderr=subprocess.PIPE, text=True)

#     def parse_output(process):
#         while True:
#             line = process.stderr.readline()
#             if not line:
#                 break

#             # Custom parsing logic to extract timestamps can be placed here
#             print(line)  # Example: output raw line for demonstration

#     # Run the parser in a separate thread to avoid blocking
#     parser_thread = threading.Thread(target=parse_output, args=(process,))
#     parser_thread.start()

#     # Wait for the thread to finish if necessary, or it can run indefinitely
#     parser_thread.join()
