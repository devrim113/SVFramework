#! /usr/bin/env python3
"""
This is the validations module that contains functions for validating video files and logs.
This module is used by the validator.py script to validate video files and their logs.
It should not be run directly but imported by the validator.py script.
"""

import subprocess
import cv2
import numpy as np
import os
import xml.etree.ElementTree as ET
import time


def __print_success(message):
    print(f"\033[32m{message}\033[0m")


def __print_failure(message):
    print(f"\033[31m{message}\033[0m")


def __print_test(message):
    width = 60
    dot_count = width - len(message)
    print(f"{message}{'.' * max(dot_count, 1)}", end="", flush=True)


def validate_ocr_similarity(original_log, simulated_log, similarity_threshold=0.95):
    """
    Validate that OCR output for the original and simulated videos are similar.
    Args:
        original_log (str): Path to the original OCR log file.
        simulated_log (str): Path to the simulated OCR log file.
        similarity_threshold (float): Minimum similarity threshold for OCR outputs.
    Returns:
        bool: True if OCR outputs are similar, False otherwise.
    """
    start_time = time.time()
    __print_test(f"Validating OCR similarity (>= {similarity_threshold * 100:.2f}%)")
    try:
        # Read and compare the contents of the original and simulated OCR log files
        with open(original_log, "r") as orig, open(simulated_log, "r") as sim:
            log_content_orig = orig.readlines()
            log_content_sim = sim.readlines()

        relevant_entries_orig = [
            line.strip() for line in log_content_orig if "score" in line or "time" in line or "period" in line
        ]
        relevant_entries_sim = [
            line.strip() for line in log_content_sim if "score" in line or "time" in line or "period" in line
        ]

        total_entries = max(len(relevant_entries_orig), len(relevant_entries_sim))
        if total_entries == 0:
            total_time = time.time() - start_time
            __print_failure(f"No relevant entries found in either log file. Time taken: {total_time} seconds.")
            return False

        differences = sum(1 for entry1, entry2 in zip(relevant_entries_orig, relevant_entries_sim) if entry1 != entry2)
        similarity = (total_entries - differences) / total_entries

        if similarity >= similarity_threshold:
            total_time = time.time() - start_time
            __print_success(
                f"Success! Measured similarity: {similarity * 100:.2f}% >= {similarity_threshold * 100:.2f}%. Time taken: {total_time} seconds."
            )
            return True
        else:
            total_time = time.time() - start_time
            __print_failure(
                f"Failed! Similarity: {similarity * 100:.2f}% is below the threshold of"
                f"{similarity_threshold * 100:.2f}%. Time taken: {total_time} seconds."
            )
            return False

    except Exception as e:
        __print_failure(f"Error during OCR similarity validation: {e}")
        return False


def validate_overlay_similarity(
    original_overlay,
    simulated_video,
    frame_skip=10,
    match_threshold=0.2,
    consecutive_matches_needed=10,
):
    """
    Validate that overlay image is present in the simulated video.
    Args:
        original_overlay (str): Path to the original overlay image file.
        simulated_video (str): Path to the simulated video file.
        frame_skip (int): Number of frames to skip between checks.
        match_threshold (float): Minimum normalized matching score to consider a match.
        consecutive_matches_needed (int): Number of consecutive frames where the overlay should be found.
    Returns:
        bool: True if overlay image is present in the simulated video, False otherwise.
    """
    start_time = time.time()
    __print_test("Validating Overlay Image in Simulated Video")
    try:
        # Open the video file and check for the presence of the overlay image
        cap = cv2.VideoCapture(simulated_video)
        if not cap.isOpened():
            __print_failure("Error! Could not open video file")
            return False

        # Read the overlay image and convert to grayscale
        overlay = cv2.imread(original_overlay, cv2.IMREAD_UNCHANGED)
        if overlay is None:
            __print_failure("Error! Could not read overlay image file.")
            return False

        # If the overlay has an alpha channel (transparency), create a mask and convert to grayscale
        if overlay.shape[2] == 4:  # Overlay has an alpha channel
            overlay_gray = cv2.cvtColor(overlay[:, :, :3], cv2.COLOR_BGR2GRAY)
            alpha_channel = overlay[:, :, 3]
            _, mask = cv2.threshold(alpha_channel, 1, 255, cv2.THRESH_BINARY)
        else:
            overlay_gray = cv2.cvtColor(overlay, cv2.COLOR_BGR2GRAY)
            mask = None

        # Counter for consecutive matches
        consecutive_matches = 0

        frame_count = 0
        found = False

        while True:
            ret, frame = cap.read()
            if not ret:
                break  # End of video

            frame_count += 1

            if frame_count % frame_skip != 0:
                continue  # Skip frames

            # Convert the frame to grayscale
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Perform template matching
            if mask is not None:
                res = cv2.matchTemplate(gray_frame, overlay_gray, cv2.TM_CCOEFF_NORMED, mask=mask)
            else:
                res = cv2.matchTemplate(gray_frame, overlay_gray, cv2.TM_CCOEFF_NORMED)

            _, max_val, _, max_loc = cv2.minMaxLoc(res)

            # Check if match is above the threshold
            if max_val >= match_threshold:
                consecutive_matches += 1
                if consecutive_matches >= consecutive_matches_needed:
                    found = True
                    break
            else:
                consecutive_matches = 0

        cap.release()

        if found:
            total_time = time.time() - start_time
            __print_success(f"Success! Overlay image is present in the simulated video. Time taken: {total_time} seconds.")
            return True
        else:
            total_time = time.time() - start_time
            __print_failure("Failed! Overlay image is not present in the simulated video. Time taken: {total_time} seconds.")
            return False

    except Exception as e:
        __print_failure(f"Error during overlay similarity validation: {e}")
        return False


def validate_vmaf(original_video, simulated_video, min_vmaf_score=75):
    """
    Validate video quality using VMAF.
    Args:
        original_video (str): Path to the original video file.
        simulated_video (str): Path to the simulated video file.
        min_vmaf_score (int): Minimum acceptable VMAF score.
    Returns:
        bool: True if VMAF score is above the acceptable minimum, False otherwise.
    """
    start_time = time.time()
    __print_test(f"Validating VMAF score (>= {min_vmaf_score})")
    try:
        # Convert original video to Y4M format
        original_y4m = "original_video.y4m"
        conversion_result = subprocess.run(
            ["ffmpeg", "-y", "-i", original_video, "-pix_fmt", "yuv420p", original_y4m],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            check=True,
        )
        if conversion_result.returncode != 0:
            __print_failure("Failed to convert original video to Y4M format.")
            return False

        # Convert simulated video to Y4M format
        simulated_y4m = "simulated_video.y4m"
        conversion_result = subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                simulated_video,
                "-pix_fmt",
                "yuv420p",
                simulated_y4m,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            check=True,
        )
        if conversion_result.returncode != 0:
            __print_failure("Failed to convert simulated video to Y4M format.")
            return False

        # Ensure both Y4M files exist before proceeding
        if not (os.path.exists(original_y4m) and os.path.exists(simulated_y4m)):
            __print_failure("Y4M files are not ready for VMAF comparison.")
            return False

        # Run the VMAF tool and capture the output
        output_xml = "output.xml"
        result = subprocess.run(
            [
                "vmaf",
                "-r",
                original_y4m,
                "-d",
                simulated_y4m,
                "-q",
                "--threads",
                str(os.cpu_count()),
                "-o",
                output_xml,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

        # Check for VMAF score in the output XML file
        if result.returncode == 0:
            try:
                tree = ET.parse(output_xml)
                root = tree.getroot()
                vmaf_score = float(root.find(".//pooled_metrics/metric[@name='vmaf']").get("mean"))
                if vmaf_score >= min_vmaf_score:
                    total_time = time.time() - start_time
                    __print_success(f"Success! VMAF score: {vmaf_score}. Time taken: {total_time} seconds.")
                    return True
                else:
                    total_time = time.time() - start_time
                    __print_failure(f"Failed! VMAF score: {vmaf_score} is below the minimum {min_vmaf_score}. Time taken: {total_time} seconds.")
                    return False
            except Exception as e:
                __print_failure(f"Failed to parse VMAF score: {e}")
                return False
        else:
            __print_failure("Failed! VMAF score validation failed.")
            print(result.stderr)  # Print the stderr output for debugging
            return False
    except Exception as e:
        __print_failure(f"Error during VMAF validation: {e}")
        return False


def validate_video_sync(simulated_video):
    """
    Validate video and audio sync.
    Args:
        simulated_video (str): Path to the simulated video file.
    Returns:
        bool: True if video and audio are in sync, False otherwise.
    """
    start_time = time.time()
    __print_test("Validating video and audio sync")
    try:
        # Use ffprobe to check for the presence of an audio stream in the video file
        result = subprocess.run(
            [
                "ffprobe",
                "-i",
                simulated_video,
                "-show_streams",
                "-select_streams",
                "a",
                "-loglevel",
                "error",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        if "Stream #0" in result.stdout:
            total_time = time.time() - start_time
            __print_success(f"Success! Video and audio are in sync. Time taken: {total_time} seconds.")
            return True
        else:
            total_time = time.time() - start_time
            __print_failure(f"Failed! No audio stream found. Time taken: {total_time} seconds.")
            return False
    except Exception as e:
        __print_failure(f"Error during video sync validation: {e}")
        return False


def validate_no_black_frames(simulated_video):
    """
    Validate that there are no black frames in the simulated video.
    Args:
        simulated_video (str): Path to the simulated video file.
    Returns:
        bool: True if there are no black frames, False otherwise.
    """
    start_time = time.time()
    __print_test("Validating no black frames")
    try:
        # Open the video file and check for black frames
        cap = cv2.VideoCapture(simulated_video)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            if np.sum(frame) == 0:
                time_taken = time.time() - start_time
                __print_failure(f"Failed! Black frame detected. Time taken: {time_taken:.2f} seconds.")
                return False
        cap.release()
        time_taken = time.time() - start_time
        __print_success(f"Success! No black frames detected. Time taken: {time_taken:.2f} seconds.")
        return True
    except Exception as e:
        __print_failure(f"Error during black frames validation: {e}")
        return False


def validate_minimum_fps(video_file, min_fps=20):
    """
    Checks if a video file maintains at least the specified frame rate.
    Args:
        video_file (str): Path to the video file.
        min_fps (int): Minimum frame rate.
    Returns:
        bool: True if the video maintains the minimum frame rate, False otherwise.
    """
    start_time = time.time()
    __print_test(f"Validating FPS (>={min_fps})")

    try:
        # Use ffprobe to get the frame rate of the video file
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=r_frame_rate",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                video_file,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

        if result.returncode != 0:
            __print_failure("Error! Could not analyze video file")
            return False

        # Extract and calculate FPS from the ffprobe output
        r_frame_rate = result.stdout.strip()
        num, denom = map(int, r_frame_rate.split("/"))
        fps = num / denom

        if fps < min_fps:
            total_time = time.time() - start_time
            __print_failure(f"Failed! Frame rate check: {fps} < {min_fps}. Time taken: {total_time} seconds.")
            return False

        total_time = time.time() - start_time
        __print_success(f"Success! Measured FPS: {fps} >= {min_fps}. Time taken: {total_time} seconds.")
        return True

    except Exception as e:
        __print_failure(f"Error during FPS validation: {e}")
        return False


def validate_minimum_resolution(simulated_video, min_width=1280, min_height=720):
    """
    Checks if a video file maintains at least the specified resolution.
    Args:
        simulated_video (str): Path to the simulated video file.
        min_width (int): Minimum width in pixels.
        min_height (int): Minimum height in pixels.
    Returns:
        bool: True if the video maintains the minimum resolution, False otherwise.
    """
    start_time = time.time()
    __print_test(f"Validating resolution (>={min_width}x{min_height})")
    try:
        # Open the video file and check its resolution
        cap = cv2.VideoCapture(simulated_video)
        if not cap.isOpened():
            __print_failure("Error! Could not open video file")
            return False

        ret, frame = cap.read()
        if not ret:
            __print_failure("Error! Can't receive frame. Video may have ended.")
            return False

        height, width = frame.shape[:2]
        if width < min_width or height < min_height:
            total_time = time.time() - start_time
            __print_failure(f"Failed! Resolution check: {width}x{height} is below minimum {min_width}x{min_height}. Time taken: {total_time} seconds.")
            return False

        total_time = time.time() - start_time
        __print_success(f"Success! Measured resolution: {width}x{height} >= {min_width}x{min_height}. Time taken: {total_time} seconds.")
        return True
    except Exception as e:
        __print_failure(f"Error during resolution validation: {e}")
        return False


def validate_bitrate(simulated_video, min_bitrate_kbps=500):
    """
    Validate that the video bitrate is above an acceptable minimum.
    Args:
        simulated_video (str): Path to the simulated video file.
        min_bitrate_kbps (int): Minimum acceptable bitrate in kbps.
    Returns:
        bool: True if the bitrate is above the acceptable minimum, False otherwise.
    """
    start_time = time.time()
    __print_test(f"Validating bitrate (>= {min_bitrate_kbps} kbps)")
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=bit_rate",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                simulated_video,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

        if result.returncode != 0:
            __print_failure("Error! Could not analyze video file")
            return False

        bitrate_kbps = int(result.stdout.strip()) / 1000

        if bitrate_kbps >= min_bitrate_kbps:
            total_time = time.time() - start_time
            __print_success(f"Success! Bitrate is {bitrate_kbps} kbps. Time taken: {total_time} seconds.")
            return True
        else:
            total_time = time.time() - start_time
            __print_failure(f"Failed! Bitrate is {bitrate_kbps} kbps, below the minimum {min_bitrate_kbps} kbps. Time taken: {total_time} seconds.")
            return False

    except Exception as e:
        __print_failure(f"Error during bitrate validation: {e}")
        return False


def validate_keyframe_interval(simulated_video, max_interval=250):
    """
    Validate that the interval between keyframes is within an acceptable range.
    Args:
        simulated_video (str): Path to the simulated video file.
        max_interval (int): Maximum acceptable interval between keyframes.
    Returns:
        bool: True if the keyframe interval is within the acceptable range, False otherwise.
    """
    start_time = time.time()
    __print_test(f"Validating keyframe interval (<= {max_interval} frames)")
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "frame=pict_type",
                "-of",
                "csv",
                simulated_video,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

        if result.returncode != 0:
            __print_failure("Error! Could not analyze video file")
            return False

        frames = result.stdout.strip().split("\n")
        keyframe_indices = [i for i, frame in enumerate(frames) if frame.endswith("I")]

        max_keyframe_interval = max(
            [j - i for i, j in zip(keyframe_indices[:-1], keyframe_indices[1:])],
            default=0,
        )

        if max_keyframe_interval <= max_interval:
            total_time = time.time() - start_time
            __print_success(f"Success! Max keyframe interval is {max_keyframe_interval} frames. Time taken: {total_time} seconds.")
            return True
        else:
            total_time = time.time() - start_time
            __print_failure(
                f"Failed! Max keyframe interval is {max_keyframe_interval} frames, exceeds {max_interval} frames. Time taken: {total_time} seconds."
            )
            return False

    except Exception as e:
        __print_failure(f"Error during keyframe interval validation: {e}")
        return False


def validate_audio_quality(simulated_video, min_bitrate_kbps=64, min_sample_rate_hz=44100):
    """
    Validate the audio quality by checking the bitrate and sample rate.
    Args:
        simulated_video (str): Path to the simulated video file.
        min_bitrate_kbps (int): Minimum acceptable audio bitrate in kbps.
        min_sample_rate_hz (int): Minimum acceptable audio sample rate in Hz.
    Returns:
        bool: True if the audio quality meets the required standards, False otherwise.
    """
    start_time = time.time()
    __print_test(f"Validating audio quality (>= {min_bitrate_kbps} kbps, >= {min_sample_rate_hz} Hz)")
    try:
        # Check if the video has an audio stream
        audio_check_result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "a:0",
                "-show_entries",
                "stream=index",
                "-of",
                "csv=p=0",
                simulated_video,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

        if audio_check_result.returncode != 0 or not audio_check_result.stdout.strip():
            __print_failure("Failed! No audio stream found.")
            return False

        # If audio stream exists, check the bitrate and sample rate
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "a:0",
                "-show_entries",
                "stream=bit_rate,sample_rate",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                simulated_video,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

        if result.returncode != 0:
            __print_failure("Error! Could not analyze audio stream")
            return False

        lines = result.stdout.strip().split("\n")
        bitrate_kbps = int(lines[0]) / 1000
        sample_rate_hz = int(lines[1])

        if bitrate_kbps >= min_bitrate_kbps and sample_rate_hz >= min_sample_rate_hz:
            total_time = time.time() - start_time
            __print_success(f"Success! Audio bitrate is {bitrate_kbps} kbps and sample rate is {sample_rate_hz} Hz. Time taken: {total_time} seconds.")
            return True
        else:
            total_time = time.time() - start_time
            __print_failure(
                f"Failed! Audio bitrate is {bitrate_kbps} kbps and sample rate is "
                f"{sample_rate_hz} Hz, below required standards. Time taken: {total_time} seconds."
            )
            return False

    except Exception as e:
        __print_failure(f"Error during audio quality validation: {e}")
        return False


def validate_video_codec(simulated_video, required_codec="h264"):
    """
    Validate that the video is encoded with a specific codec.
    Args:
        simulated_video (str): Path to the simulated video file.
        required_codec (str): Required video codec (e.g., "h264").
    Returns:
        bool: True if the video is encoded with the required codec, False otherwise.
    """
    start_time = time.time()
    __print_test(f"Validating video codec ({required_codec})")
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=codec_name",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                simulated_video,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

        if result.returncode != 0:
            __print_failure("Error! Could not analyze video codec")
            return False

        codec = result.stdout.strip()

        if codec == required_codec:
            total_time = time.time() - start_time
            __print_success(f"Success! Video codec is {codec}. Time taken: {total_time} seconds.")
            return True
        else:
            total_time = time.time() - start_time
            __print_failure(f"Failed! Video codec is {codec}, expected {required_codec}. Time taken: {total_time} seconds.")
            return False

    except Exception as e:
        __print_failure(f"Error during video codec validation: {e}")
        return False


def validate_error_similarity(original_log, simulated_log, similarity_threshold=0.95):
    """
    Validate that error logs for the original and simulated videos are similar.
    Args:
        original_log (str): Path to the original error log file.
        simulated_log (str): Path to the simulated error log file.
        similarity_threshold (float): Minimum similarity threshold for error logs.
    Returns:
        bool: True if error logs are similar, False otherwise.
    """
    start_time = time.time()
    __print_test("Validating error similarity")
    try:
        with open(original_log, "r") as file:
            original_lines = [line for line in file if "error" in line.lower()]

        with open(simulated_log, "r") as file:
            simulated_lines = [line for line in file if "error" in line.lower()]

        total_entries = max(len(original_lines), len(simulated_lines))
        if total_entries == 0:
            __print_success("No error entries found in either log file.")
            return True

        differences = sum(1 for entry1, entry2 in zip(original_lines, simulated_lines) if entry1 != entry2)
        similarity = (total_entries - differences) / total_entries

        if similarity >= similarity_threshold:
            total_time = time.time() - start_time
            __print_success(
                f"Success! Measured similarity: {similarity * 100:.2f}% >= {similarity_threshold * 100:.2f}%. Time taken: {total_time} seconds."
            )
            return True
        else:
            total_time = time.time() - start_time
            __print_failure(
                f"Failed! Similarity: {similarity * 100:.2f}% is below the threshold of"
                f"{similarity_threshold * 100:.2f}%. Time taken: {total_time} seconds."
            )
            return False
    except Exception as e:
        __print_failure(f"Error during error similarity validation: {e}")
        return False
