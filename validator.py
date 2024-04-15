#! /usr/bin/env python3
"""
This is the main script for running validations on the simulated RTSP streams.
The script takes a streaming URL as an argument and validates the stream by checking its accessibility using ffprobe.
Usage: python validator.py <streaming_url>
"""

import sys
import validations

if __name__ == "__main__":
    # Get the url from the command line arguments
    if len(sys.argv) > 1:
        streaming_url = sys.argv[1]
    else:
        print("Please provide the streaming URL as an argument.")
        print("Usage: python validation.py <streaming_url>")
        sys.exit(1)

    validation_types = sorted(
        [
            func
            for func in dir(validations)
            if callable(getattr(validations, func)) and not func.startswith("__")
        ],
        key=lambda x: getattr(validations, x).__code__.co_firstlineno,
    )

    for func in validation_types:
        assert getattr(validations, func)(streaming_url), f"Validation {func} failed."

    print("All checks passed for video.\n")
