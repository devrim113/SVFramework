#!/usr/bin/env python3
"""
This is the main script for running validations on video files and their logs.
The script takes a folder containing video files, a folder containing video logs, a folder containing OCR logs,
and a VMAF option as arguments, and validates them.
Usage: python validator.py <video_folder> <video_logs> <ocr_logs> <vmaf_option>
"""

import os
import sys
import subprocess
import time
import validations


def has_audio_stream(video_file):
    """
    Check if the video file contains an audio stream.
    Args:
        video_file (str): Path to the video file.
    Returns:
        bool: True if the video contains an audio stream, False otherwise.
    """
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-i",
                video_file,
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
        return "Stream #0" in result.stdout
    except Exception as e:
        print(f"\033[31mError checking for audio stream: {e}\033[0m")
        return False


def validate_video_files_and_logs(original_video, simulated_video, video_logs, ocr_logs, original_overlay, vmaf_option):
    validation_types = sorted(
        [func for func in dir(validations) if callable(getattr(validations, func)) and not func.startswith("__")],
        key=lambda x: getattr(validations, x).__code__.co_firstlineno,
    )

    error_count = 0
    failed_validations = []

    # Check if the simulated video has an audio stream
    simulated_video_has_audio = has_audio_stream(simulated_video)

    for func in validation_types:
        try:
            if func == "validate_ocr_similarity":
                original_log = os.path.join(ocr_logs, "original_ocr.log")
                simulated_log = os.path.join(ocr_logs, "simulated_ocr.log")
                result = getattr(validations, func)(original_log, simulated_log)
            elif func == "validate_error_similarity":
                original_log = os.path.join(video_logs, "original_video.log")
                simulated_log = os.path.join(video_logs, "simulated_video.log")
                result = getattr(validations, func)(original_log, simulated_log)
            elif func == "validate_vmaf":
                if vmaf_option == 0:
                    print(
                        f"\033[33mSkipping {func} - VMAF validation disabled by argument in run-command."
                        "Change the 0 to 1 to activate.\033[0m"
                    )
                    continue
                else:
                    result = getattr(validations, func)(original_video, simulated_video)
            elif func in ["validate_video_sync", "validate_audio_quality"]:
                if simulated_video_has_audio:
                    result = getattr(validations, func)(simulated_video)
                else:
                    print(f"\033[33mSkipping {func} - no audio stream found in the simulated video.\033[0m")
                    continue
            elif func == "validate_overlay_similarity":
                result = getattr(validations, func)(original_overlay, simulated_video)
            else:
                result = getattr(validations, func)(simulated_video)

            if not result:
                failed_validations.append(func)
                error_count += 1
        except Exception as e:
            print(f"\033[31mError during validation '{func}': {e}\033[0m")
            error_count += 1

    if error_count == 0:
        print("\033[32mSuccess! All validations passed.\033[0m")
    else:
        print(f"\033[31mErrors found: {error_count}. Failed validations: {', '.join(failed_validations)}\033[0m")


if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Please provide the video folder, video logs folder, OCR logs folder, and the VMAF option as arguments.")
        print("Usage: python validator.py <video_folder> <video_logs> <ocr_logs> <overlay_image> <vmaf_option (0, 1)>")
        sys.exit(1)

    video_folder = sys.argv[1]
    video_logs_folder = sys.argv[2]
    ocr_logs_folder = sys.argv[3]
    overlay_image = sys.argv[4]
    vmaf_option = int(sys.argv[5])

    # Get the paths of the two videos in the video folder
    video_files = [
        os.path.join(video_folder, f) for f in os.listdir(video_folder) if f.endswith((".mp4", ".mkv", ".avi", ".ts"))
    ]
    if len(video_files) != 2:
        print("The video folder must contain exactly two video files.")
        sys.exit(1)

    original_video_file_path = video_files[0]
    simulated_video_file_path = video_files[1]

    start_time = time.time()

    validate_video_files_and_logs(
        original_video_file_path,
        simulated_video_file_path,
        video_logs_folder,
        ocr_logs_folder,
        overlay_image,
        vmaf_option,
    )

    # Calculate and print the total duration
    total_duration = time.time() - start_time
    print(f"Total test duration: {total_duration:.2f} seconds.")

    # Delete all .y4m, .yuv, and .xml files in the current directory
    for file in os.listdir():
        if file.endswith(".y4m") or file.endswith(".yuv") or file.endswith(".xml"):
            os.remove(file)
