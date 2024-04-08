import subprocess
import sys


def validate_stream_running(url):
    """
    Check if the RTSP stream is accessible using ffprobe.
    """
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
    return result.returncode == 0


if __name__ == "__main__":
    # Get the url from the command line arguments
    if len(sys.argv) > 1:
        streaming_url = sys.argv[1]
    else:
        print("Please provide the streaming URL as an argument.")
        print("Usage: python validation.py <streaming_url>")
        sys.exit(1)

    # Assert that the stream is running
    assert validate_stream_running(
        streaming_url
    ), "Stream is not running or inaccessible."

    print("Stream check passed. The stream is running.")
