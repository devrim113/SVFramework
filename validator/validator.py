#!/usr/bin/env python3
"""
This is the main script for running validations on video files and their logs.
The script takes a video file path and corresponding log file paths as arguments and validates them.
Usage: python validator.py <original_video_file_path> <simulated_video_file_path> <original_log_file_path>
<simulated_log_file_path> <vmaf_option>
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


def validate_video_files_and_logs(
    original_video, simulated_video, original_log, simulated_log, vmaf_option
):
    validation_types = sorted(
        [
            func
            for func in dir(validations)
            if callable(getattr(validations, func)) and not func.startswith("__")
        ],
        key=lambda x: getattr(validations, x).__code__.co_firstlineno,
    )

    error_count = 0
    failed_validations = []

    # Check if the simulated video has an audio stream
    simulated_video_has_audio = has_audio_stream(simulated_video)

    for func in validation_types:
        try:
            if func in ["validate_ocr_similarity", "validate_overlay_similarity"]:
                result = getattr(validations, func)(original_log, simulated_log)
            elif func == "validate_vmaf":
                if vmaf_option == 0:
                    print(f"\033[33mSkipping {func} - VMAF validation disabled.\033[0m")
                    continue
                else:
                    result = getattr(validations, func)(original_video, simulated_video)
            elif func in ["validate_video_sync", "validate_audio_quality"]:
                if simulated_video_has_audio:
                    result = getattr(validations, func)(simulated_video)
                else:
                    print(
                        f"\033[33mSkipping {func} - no audio stream found in the simulated video.\033[0m"
                    )
                    continue
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
        print(
            f"\033[31mErrors found: {error_count}. Failed validations: {', '.join(failed_validations)}\033[0m"
        )


if __name__ == "__main__":
    if len(sys.argv) != 6:
        print(
            "Please provide the original and simulated video file paths, "
            "original and simulated log file paths, and the VMAF option as arguments."
        )
        print(
            "Usage: python validator.py <original_video_file_path> "
            "<simulated_video_file_path> <original_log_file_path> <simulated_log_file_path> <vmaf_option (0, 1)>"
        )
        sys.exit(1)

    original_video_file_path = sys.argv[1]
    simulated_video_file_path = sys.argv[2]
    original_log_file_path = sys.argv[3]
    simulated_log_file_path = sys.argv[4]
    vmaf_option = int(sys.argv[5])

    start_time = time.time()

    validate_video_files_and_logs(
        original_video_file_path,
        simulated_video_file_path,
        original_log_file_path,
        simulated_log_file_path,
        vmaf_option,
    )

    # Calculate and print the total duration
    total_duration = time.time() - start_time
    print(f"Total test duration: {total_duration:.2f} seconds.")

    # Delete all .y4m, .yuv, and .xml files in the current directory
    for file in os.listdir():
        if file.endswith(".y4m") or file.endswith(".yuv") or file.endswith(".xml"):
            os.remove(file)
