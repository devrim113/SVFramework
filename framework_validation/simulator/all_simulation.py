import subprocess
import sys


def __print_success(message):
    print(f"\033[32m{message}\033[0m")


def __print_failure(message):
    print(f"\033[31m{message}\033[0m")


def __print_test(message):
    width = 60
    dot_count = width - len(message)
    print(f"{message}{'.' * max(dot_count, 1)}", end="", flush=True)


def check_stream_accessible(url):
    __print_test("Checking if stream is accessible")
    output = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height",
            "-of",
            "csv=s=x:p=0",
            url,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    output = output.stdout.decode("utf-8")
    if "N/A" in output:
        __print_failure("Failed! Stream not accessible.")
        return False
    __print_success("Success! Stream accessible.")
    return True


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 network_simulation.py <url>")
        sys.exit(1)

    url = sys.argv[1]
    check_stream_accessible(url)
