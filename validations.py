import subprocess
import cv2
import numpy as np
import os
import xml.etree.ElementTree as ET


def __print_success(message):
    print(f"\033[32m{message}\033[0m")


def __print_failure(message):
    print(f"\033[31m{message}\033[0m")


def __print_test(message):
    width = 60
    dot_count = width - len(message)
    print(f"{message}{'.' * max(dot_count, 1)}", end="", flush=True)


def validate_ocr_similarity(original_log, simulated_log):
    """
    Validate that OCR output for the original and simulated videos are similar.
    Args:
        original_log (str): Path to the original OCR log file.
        simulated_log (str): Path to the simulated OCR log file.
    Returns:
        bool: True if OCR outputs are similar, False otherwise.
    """
    __print_test("Validating OCR similarity")
    try:
        # Read and compare the contents of the original and simulated OCR log files
        with open(original_log, "r") as orig, open(simulated_log, "r") as sim:
            if orig.read() == sim.read():
                __print_success("Success! OCR outputs are similar.")
                return True
            else:
                __print_failure("Failed! OCR outputs are not similar.")
                return False
    except Exception as e:
        __print_failure(f"Error during OCR similarity validation: {e}")
        return False


def validate_overlay_similarity(original_log, simulated_log):
    """
    Validate that overlay model output for the original and simulated videos are similar.
    Args:
        original_log (str): Path to the original overlay log file.
        simulated_log (str): Path to the simulated overlay log file.
    Returns:
        bool: True if overlay outputs are similar, False otherwise.
    """
    __print_test("Validating overlay similarity")
    try:
        # Read and compare the contents of the original and simulated overlay log files
        with open(original_log, "r") as orig, open(simulated_log, "r") as sim:
            if orig.read() == sim.read():
                __print_success("Success! Overlay outputs are similar.")
                return True
            else:
                __print_failure("Failed! Overlay outputs are not similar.")
                return False
    except Exception as e:
        __print_failure(f"Error during overlay similarity validation: {e}")
        return False


def validate_qos_metrics(simulated_video):
    """
    Validate QoS metrics such as resolution.
    Args:
        simulated_video (str): Path to the simulated video file.
    Returns:
        bool: True if QoS metrics are within acceptable thresholds, False otherwise.
    """
    __print_test("Validating QoS metrics")
    try:
        # Open the video file and check its resolution
        cap = cv2.VideoCapture(simulated_video)
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        if width >= 1280 and height >= 720:
            __print_success(f"Success! Resolution is {width}x{height}.")
            return True
        else:
            __print_failure(
                f"Failed! Resolution is {width}x{height}, which is below the acceptable threshold."
            )
            return False
    except Exception as e:
        __print_failure(f"Error during QoS metrics validation: {e}")
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
    __print_test(f"Validating VMAF score (>= {min_vmaf_score})")
    try:
        # Convert original video to Y4M format
        original_y4m = "original_video.y4m"
        conversion_result = subprocess.run(
            ["ffmpeg", "-y", "-i", original_video, "-pix_fmt", "yuv420p", original_y4m],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            check=True
        )
        if conversion_result.returncode != 0:
            __print_failure("Failed to convert original video to Y4M format.")
            return False

        # Convert simulated video to Y4M format
        simulated_y4m = "simulated_video.y4m"
        conversion_result = subprocess.run(
            ["ffmpeg", "-y", "-i", simulated_video, "-pix_fmt", "yuv420p", simulated_y4m],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            check=True
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
            ["vmaf", "-r", original_y4m, "-d", simulated_y4m, "-q", "--threads", str(os.cpu_count()), "-o", output_xml],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )

        # Check for VMAF score in the output XML file
        if result.returncode == 0:
            try:
                tree = ET.parse(output_xml)
                root = tree.getroot()
                vmaf_score = float(root.find(".//pooled_metrics/metric[@name='vmaf']").get('mean'))
                if vmaf_score >= min_vmaf_score:
                    __print_success(f"Success! VMAF score: {vmaf_score}")
                    return True
                else:
                    __print_failure(f"Failed! VMAF score: {vmaf_score} is below the minimum {min_vmaf_score}")
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
            __print_success("Success! Video and audio are in sync.")
            return True
        else:
            __print_failure("Failed! No audio stream found.")
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
    __print_test("Validating no black frames")
    try:
        # Open the video file and check for black frames
        cap = cv2.VideoCapture(simulated_video)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            if np.sum(frame) == 0:
                __print_failure("Failed! Black frame detected.")
                return False
        cap.release()
        __print_success("Success! No black frames detected.")
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
            __print_failure(f"Failed! Frame rate check: {fps} < {min_fps}")
            return False

        __print_success(f"Success! Measured FPS: {fps} >= {min_fps}.")
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
            __print_failure(
                f"Failed! Resolution check: {width}x{height} is below minimum {min_width}x{min_height}"
            )
            return False

        __print_success(
            f"Success! Measured resolution: {width}x{height} >= {min_width}x{min_height}."
        )
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
            __print_success(f"Success! Bitrate is {bitrate_kbps} kbps.")
            return True
        else:
            __print_failure(
                f"Failed! Bitrate is {bitrate_kbps} kbps, below the minimum {min_bitrate_kbps} kbps"
            )
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
            __print_success(
                f"Success! Max keyframe interval is {max_keyframe_interval} frames."
            )
            return True
        else:
            __print_failure(
                f"Failed! Max keyframe interval is {max_keyframe_interval} frames, exceeds {max_interval} frames."
            )
            return False

    except Exception as e:
        __print_failure(f"Error during keyframe interval validation: {e}")
        return False


def validate_audio_quality(
    simulated_video, min_bitrate_kbps=64, min_sample_rate_hz=44100
):
    """
    Validate the audio quality by checking the bitrate and sample rate.
    Args:
        simulated_video (str): Path to the simulated video file.
        min_bitrate_kbps (int): Minimum acceptable audio bitrate in kbps.
        min_sample_rate_hz (int): Minimum acceptable audio sample rate in Hz.
    Returns:
        bool: True if the audio quality meets the required standards, False otherwise.
    """
    __print_test(
        f"Validating audio quality (>= {min_bitrate_kbps} kbps, >= {min_sample_rate_hz} Hz)"
    )
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
            __print_success(
                f"Success! Audio bitrate is {bitrate_kbps} kbps and sample rate is {sample_rate_hz} Hz"
            )
            return True
        else:
            __print_failure(
                f"Failed! Audio bitrate is {bitrate_kbps} kbps and sample rate is "
                "{sample_rate_hz} Hz, below required standards"
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
            __print_success(f"Success! Video codec is {codec}.")
            return True
        else:
            __print_failure(
                f"Failed! Video codec is {codec}, expected {required_codec}."
            )
            return False

    except Exception as e:
        __print_failure(f"Error during video codec validation: {e}")
        return False
