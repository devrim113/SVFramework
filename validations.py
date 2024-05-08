#! /usr/bin/env python3
"""
This is the validations module for defining different validation types for the input data.
It should not be run, but imported by the validator script.
"""

import subprocess
import cv2
import time


def __print_success(message):
    print(f"\033[32m{message}\033[0m")


def __print_failure(message):
    print(f"\033[31m{message}\033[0m")


def __print_test(message):
    width = 40
    dot_count = width - len(message)
    print(f"{message}{'.' * max(dot_count, 1)}", end="", flush=True)


def stream_running(url):
    """
    Check if the RTSP stream is accessible using ffprobe.
    Args:
        url: The URL of the RTSP stream to validate.
    Returns:
        bool: True if the stream is accessible, False otherwise.
    """
    __print_test("Running and accessible")
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
        __print_success("Success! Stream is running and accessible.")
        return True
    __print_failure("Failed! Stream is not running or accessible.")
    return False


def minimum_fps(rtsp_url, duration=10, min_fps=20):
    """
    Checks if a live RTSP stream maintains at least the specified frame rate.
    Args:
        rtsp_url (str): URL of the RTSP stream.
        duration (int): Duration in seconds to monitor the stream.
        min_fps (int): Minimum frame rate.
    Returns:
        bool: True if the stream maintains the minimum frame rate, False otherwise.
    """
    __print_test(f"Minimum FPS of {min_fps}")
    cap = cv2.VideoCapture(rtsp_url)
    if not cap.isOpened():
        __print_failure("Error! Could not open stream")
        return False

    start_time = time.time()
    frame_count = 0
    try:
        while time.time() - start_time < duration:
            ret, _ = cap.read()
            if not ret:
                __print_failure("Error! Can't receive frame. Stream may have ended.")
                return False
            frame_count += 1
    finally:
        cap.release()
        cv2.destroyAllWindows()

    fps = frame_count / duration
    if fps < min_fps:
        __print_failure(f"Failed! Frame rate check: {fps} < {min_fps}")
        return False

    __print_success(f"Success! Measured FPS: {fps} >= {min_fps}")
    return True


def minimum_resolution(rtsp_url, duration=10, min_width=1280, min_height=720):
    """
    Checks if a live RTSP stream maintains at least the specified resolution.
    Args:
        rtsp_url (str): URL of the RTSP stream.
        duration (int): Duration in seconds to monitor the stream.
        min_width (int): Minimum width in pixels.
        min_height (int): Minimum height in pixels.
    Returns:
        bool: True if the stream maintains the minimum resolution, False otherwise.
    """
    __print_test(f"Minimum resolution of {min_width}x{min_height}")
    cap = cv2.VideoCapture(rtsp_url)
    if not cap.isOpened():
        __print_failure("Error! Could not open stream")
        return False

    start_time = time.time()
    try:
        while time.time() - start_time < duration:
            ret, frame = cap.read()
            if not ret:
                __print_failure("Error! Can't receive frame. Stream may have ended.")
                return False

            height, width = frame.shape[:2]
            if width < min_width or height < min_height:
                __print_failure(
                    f"Failed! Resolution check: {width}x{height} is below minimum {min_width}x{min_height}"
                )
                return False
    finally:
        cap.release()
        cv2.destroyAllWindows()

    __print_success(
        f"Success! Measured resolution: {width}x{height} >= {min_width}x{min_height}"
    )
    return True


def not_black(rtsp_url):
    """
    Check if the RTSP stream is not black.
    Args:
        rtsp_url: The URL of the RTSP stream.
    Returns:
        bool: True if the stream is not black, False otherwise.
    """
    __print_test("Stream is not black")
    cap = cv2.VideoCapture(rtsp_url)
    if not cap.isOpened():
        __print_failure("Error! Could not open stream")
        return False

    try:
        for _ in range(10):
            ret, frame = cap.read()
            if not ret:
                __print_failure("Error! Can't receive frame. Stream may have ended.")
                return False

            # Check if the frame is not black
            if frame.mean() > 10:
                __print_success("Success! Stream is not black.")
                return True
    finally:
        cap.release()
        cv2.destroyAllWindows()

    __print_failure("Failed! Stream is black.")
    return False
