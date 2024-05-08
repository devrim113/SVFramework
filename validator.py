#! /usr/bin/env python3
"""
This is the main script for running validations on the simulated RTSP streams.
The script takes a streaming URL as an argument and validates the stream by checking its accessibility using ffprobe.
Usage: python validator.py <streaming_url>
"""

import sys
import validations

if __name__ == "__main__":
    # Get the URL from the command line arguments
    if len(sys.argv) > 1:
        streaming_url = sys.argv[1]
    else:
        print("Please provide the streaming URL as an argument.")
        print("Usage: python validator.py <streaming_url>")
        sys.exit(1)

    # Collect all validatable functions
    validation_types = sorted(
        [
            func
            for func in dir(validations)
            if callable(getattr(validations, func)) and not func.startswith("__")
        ],
        key=lambda x: getattr(validations, x).__code__.co_firstlineno,
    )

    # Count the number of validation errors
    error_count = 0
    failed_validations = []

    # Execute each validation function and check its result
    for func in validation_types:
        try:
            result = getattr(validations, func)(streaming_url)
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
