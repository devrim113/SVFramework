#! /usr/bin/env python3
"""
This is the main script for running validations on video files and their logs.
The script takes a video file path and corresponding log file paths as arguments and validates them.
Usage: python validator.py <original_video_file_path>
    <simulated_video_file_path> <original_log_file_path> <simulated_log_file_path>
"""

import os
import sys
import validations


def validate_video_files_and_logs(
    original_video, simulated_video, original_log, simulated_log
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

    for func in validation_types:
        try:
            if func in ["validate_ocr_similarity", "validate_overlay_similarity"]:
                result = getattr(validations, func)(original_log, simulated_log)
            elif func == "validate_vmaf":
                result = getattr(validations, func)(original_video, simulated_video)
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
    if len(sys.argv) != 5:
        print(
            "Please provide the original and simulated video file paths, "
            "and original and simulated log file paths as arguments."
        )
        print(
            "Usage: python validator.py <original_video_file_path> "
            "<simulated_video_file_path> <original_log_file_path> <simulated_log_file_path>"
        )
        sys.exit(1)

    original_video_file_path = sys.argv[1]
    simulated_video_file_path = sys.argv[2]
    original_log_file_path = sys.argv[3]
    simulated_log_file_path = sys.argv[4]

    validate_video_files_and_logs(
        original_video_file_path,
        simulated_video_file_path,
        original_log_file_path,
        simulated_log_file_path,
    )

    # Delete all .y4m files in the current directory
    for file in os.listdir():
        if file.endswith(".y4m") or file.endswith(".yuv") or file.endswith(".xml"):
            os.remove(file)
