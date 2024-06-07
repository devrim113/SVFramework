import sys
import os
import cv2
import subprocess
import numpy as np


def __print_success(message):
    print(f"\033[32m{message}\033[0m")


def __print_failure(message):
    print(f"\033[31m{message}\033[0m")


def __print_test(message):
    width = 60
    dot_count = width - len(message)
    print(f"{message}{'.' * max(dot_count, 1)}", end="", flush=True)


def validate_low_resolution(original_video_file, simulated_video_file):
    """
    Checks if the simulator produces a lower resolution video.
    Args:
        original_video_file (str): Path to the original video file.
        simulated_video_file (str): Path to the simualted video file.
    Returns:
        bool: True if the simulated video file has a lower resolution than the original video file, False otherwise.
    """
    __print_test("Validating Low Resolution")
    try:

        original_cap = cv2.VideoCapture(original_video_file)
        if not original_cap.isOpened():
            __print_failure("Error! Could not open video file")
            return False

        original_ret, original_frame = original_cap.read()
        if not original_ret:
            __print_failure("Error! Can't receive frame. Video may have ended.")
            return False

        original_height, original_width = original_frame.shape[:2]

        # Open the simualted video file and check its resolution
        simulated_cap = cv2.VideoCapture(simulated_video_file)
        if not simulated_cap.isOpened():
            __print_failure("Error! Could not open video file")
            return False

        simulated_ret, simulated_frame = simulated_cap.read()
        if not simulated_ret:
            __print_failure("Error! Can't receive frame. Video may have ended.")
            return False

        simulated_height, simulated_width = simulated_frame.shape[:2]

        if simulated_height >= original_height or simulated_width >= original_width:
            __print_failure(
                f"Failed! Simulated resolution: {simulated_width}x{simulated_height} >="
                "Original resolution: {original_width}x{original_height}"
            )
            return False
        __print_success(
            f"Success! Simulated resolution: {simulated_width}x{simulated_height} <="
            "Original resolution: {original_width}x{original_height}"
        )
        return True
    except Exception as e:
        __print_failure(f"Error during low resolution validation: {e}")
        return False


def validate_compression_artifacts(
    original_video_file, simulated_video_file, threshold=30
):
    """
    Checks if the simulator produces a video with compression artifacts.
    Args:
        original_video_file (str): Path to the original video file.
        simulated_video_file (str): Path to the simulated video file.
        threshold (int): PSNR threshold to consider the video as having compression artifacts.
    Returns:
        bool: True if the simulated video file has compression artifacts
              compared to the original video file, False otherwise.
    """
    __print_test("Validating Compression Artifacts")
    try:
        # Use ffmpeg to calculate PSNR between the original and simulated video
        command = [
            "ffmpeg",
            "-i",
            original_video_file,
            "-i",
            simulated_video_file,
            "-lavfi",
            "psnr",
            "-f",
            "null",
            "-",
        ]

        result = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        psnr_output = result.stderr

        # Extract PSNR value from the output
        psnr_value = None
        for line in psnr_output.split("\n"):
            if "average:" in line:
                psnr_value = float(line.split("average:")[1].split(" ")[0].strip())
                break

        if psnr_value is None:
            __print_failure("Error! PSNR value could not be determined.")
            return False

        if psnr_value < threshold:
            __print_success(
                f"Success! PSNR value: {psnr_value} indicates compression artifacts."
            )
            return True
        else:
            __print_failure(
                f"Failed! PSNR value: {psnr_value} indicates insufficient compression artifacts."
            )
            return False

    except Exception as e:
        __print_failure(f"Error during compression artifacts validation: {e}")
        return False


def validate_change_brightness(
    original_video_file, simulated_video_file, brightness_threshold=10
):
    """
    Checks if the simulator produces a video with altered brightness.
    Args:
        original_video_file (str): Path to the original video file.
        simulated_video_file (str): Path to the simulated video file.
        brightness_threshold (int): Threshold for brightness difference to consider the change significant.
    Returns:
        bool: True if the simulated video file has a different brightness
              compared to the original video file, False otherwise.
    """
    __print_test("Validating Change Brightness")
    try:
        # Open the original video file
        original_cap = cv2.VideoCapture(original_video_file)
        if not original_cap.isOpened():
            __print_failure("Error! Could not open original video file")
            return False

        # Open the simulated video file
        simulated_cap = cv2.VideoCapture(simulated_video_file)
        if not simulated_cap.isOpened():
            __print_failure("Error! Could not open simulated video file")
            return False

        original_brightness_list = []
        simulated_brightness_list = []

        # Calculate average brightness for a few frames of the original video
        while True:
            original_ret, original_frame = original_cap.read()
            if not original_ret:
                break
            original_brightness_list.append(
                cv2.cvtColor(original_frame, cv2.COLOR_BGR2GRAY).mean()
            )
            if (
                len(original_brightness_list) >= 30
            ):  # Arbitrary number of frames to check
                break

        # Calculate average brightness for a few frames of the simulated video
        while True:
            simulated_ret, simulated_frame = simulated_cap.read()
            if not simulated_ret:
                break
            simulated_brightness_list.append(
                cv2.cvtColor(simulated_frame, cv2.COLOR_BGR2GRAY).mean()
            )
            if (
                len(simulated_brightness_list) >= 30
            ):  # Arbitrary number of frames to check
                break

        original_avg_brightness = np.mean(original_brightness_list)
        simulated_avg_brightness = np.mean(simulated_brightness_list)

        if (
            abs(simulated_avg_brightness - original_avg_brightness)
            < brightness_threshold
        ):
            __print_failure(
                f"Failed! Brightness change is not significant. Original: {original_avg_brightness},"
                "Simulated: {simulated_avg_brightness}"
            )
            return False

        __print_success(
            f"Success! Brightness change is significant. Original: {original_avg_brightness}, "
            "Simulated: {simulated_avg_brightness}"
        )
        return True

    except Exception as e:
        __print_failure(f"Error during brightness validation: {e}")
        return False


def validate_blur(original_video_file, simulated_video_file):
    """
    Checks if the simulator produces a video with blur.
    Args:
        original_video_file (str): Path to the original video file.
        simulated_video_file (str): Path to the simulated video file.
    Returns:
        bool: True if the simulated video file has blur compared to the original video file, False otherwise.
    """
    try:
        # Open the original video file
        original_cap = cv2.VideoCapture(original_video_file)
        if not original_cap.isOpened():
            __print_failure("Error! Could not open original video file")
            return False

        # Open the simulated video file
        simulated_cap = cv2.VideoCapture(simulated_video_file)
        if not simulated_cap.isOpened():
            __print_failure("Error! Could not open simulated video file")
            return False

        original_blur_list = []
        simulated_blur_list = []

        # Calculate average brightness for a few frames of the original video
        while True:
            original_ret, original_frame = original_cap.read()
            if not original_ret:
                break
            original_blur_list.append(cv2.Laplacian(original_frame, cv2.CV_64F).var())
            if len(original_blur_list) >= 30:  # Arbitrary number of frames to check
                break

        # Calculate average brightness for a few frames of the simulated video
        while True:
            simulated_ret, simulated_frame = simulated_cap.read()
            if not simulated_ret:
                break
            simulated_blur_list.append(cv2.Laplacian(simulated_frame, cv2.CV_64F).var())
            if len(simulated_blur_list) >= 30:  # Arbitrary number of frames to check
                break

        original_avg_blur = np.mean(original_blur_list)
        simulated_avg_blur = np.mean(simulated_blur_list)

        if abs(simulated_avg_blur - original_avg_blur) < 10:
            __print_failure(
                f"Failed! Blur change is not significant. Original: {original_avg_blur},"
                "Simulated: {simulated_avg_blur}"
            )
            return False

        __print_success(
            f"Success! Blur change is significant. Original: {original_avg_blur}, "
            "Simulated: {simulated_avg_blur}"
        )
        return True
    except Exception as e:
        __print_failure(
            f"Error during blur validation: {e}"
        ) or simulation_name == "contrast" or simulation_name == "dynamic_contrast"
        return False


def validate_contrast(original_video_file, simulated_video_file):
    """
    Checks if the simulator produces a video with altered contrast.
    Args:
        original_video_file (str): Path to the original video file.
        simulated_video_file (str): Path to the simulated video file.
    Returns:
        bool: True if the simulated video file has a different contrast
              compared to the original video file, False otherwise.
    """
    __print_test("Validating Change Contrast")
    try:
        # Open the original video file
        original_cap = cv2.VideoCapture(original_video_file)
        if not original_cap.isOpened():
            __print_failure("Error! Could not open original video file")
            return False

        # Open the simulated video file
        simulated_cap = cv2.VideoCapture(simulated_video_file)
        if not simulated_cap.isOpened():
            __print_failure("Error! Could not open simulated video file")
            return False

        original_contrast_list = []
        simulated_contrast_list = []

        # Calculate average contrast for a few frames of the original video
        while True:
            original_ret, original_frame = original_cap.read()
            if not original_ret:
                break
            original_contrast_list.append(
                cv2.cvtColor(original_frame, cv2.COLOR_BGR2GRAY).std()
            )
            if len(original_contrast_list) >= 30:  # Arbitrary number of frames to check
                break

        # Calculate average contrast for a few frames of the simulated video
        while True:
            simulated_ret, simulated_frame = simulated_cap.read()
            if not simulated_ret:
                break
            simulated_contrast_list.append(
                cv2.cvtColor(simulated_frame, cv2.COLOR_BGR2GRAY).std()
            )
            if (
                len(simulated_contrast_list) >= 30
            ):  # Arbitrary number of frames to check
                break

        original_avg_contrast = np.mean(original_contrast_list)
        simulated_avg_contrast = np.mean(simulated_contrast_list)

        if abs(simulated_avg_contrast - original_avg_contrast) < 5:
            __print_failure(
                f"Failed! Contrast change is not significant. Original: {original_avg_contrast},"
                "Simulated: {simulated_avg_contrast}"
            )
            return False

        __print_success(
            f"Success! Contrast change is significant. Original: {original_avg_contrast},"
            "Simulated: {simulated_avg_contrast}"
        )
        return True

    except Exception as e:
        __print_failure(f"Error during contrast validation: {e}")
        return False


def validate_background_noise(original_video_file, simulated_video_file):
    """
    Checks if the simulator produces a video with background noise.
    Args:
        original_video_file (str): Path to the original video file.
        simulated_video_file (str): Path to the simulated video file.
    Returns:
        bool: True if the simulated video file has background noise compared to the original video file,
              False otherwise.
    """
    __print_test("Validating Background Noise")
    try:
        # Open the original video file
        original_cap = cv2.VideoCapture(original_video_file)
        if not original_cap.isOpened():
            __print_failure("Error! Could not open original video file")
            return False

        # Open the simulated video file
        simulated_cap = cv2.VideoCapture(simulated_video_file)
        if not simulated_cap.isOpened():
            __print_failure("Error! Could not open simulated video file")
            return False

        original_noise_list = []
        simulated_noise_list = []

        # Calculate average brightness for a few frames of the original video
        while True:
            original_ret, original_frame = original_cap.read()
            if not original_ret:
                break
            original_noise_list.append(cv2.Laplacian(original_frame, cv2.CV_64F).var())
            if len(original_noise_list) >= 30:  # Arbitrary number of frames to check
                break

        # Calculate average brightness for a few frames of the simulated video
        while True:
            simulated_ret, simulated_frame = simulated_cap.read()
            if not simulated_ret:
                break
            simulated_noise_list.append(
                cv2.Laplacian(simulated_frame, cv2.CV_64F).var()
            )
            if len(simulated_noise_list) >= 30:  # Arbitrary number of frames to check
                break

        original_avg_noise = np.mean(original_noise_list)
        simulated_avg_noise = np.mean(simulated_noise_list)

        if abs(simulated_avg_noise - original_avg_noise) < 10:
            __print_failure(
                f"Failed! Noise change is not significant. Original: {original_avg_noise},"
                "Simulated: {simulated_avg_noise}"
            )
            return False

        __print_success(
            f"Success! Noise change is significant. Original: {original_avg_noise}, "
            "Simulated: {simulated_avg_noise}"
        )
        return True

    except Exception as e:
        __print_failure(f"Error during noise validation: {e}")
        return False


def validate_horizontal_drift(original_video_file, simulated_video_file):
    """
    Checks if the simulator produces a video with horizontal drift.
    Args:
        original_video_file (str): Path to the original video file.
        simulated_video_file (str): Path to the simulated video file.
    Returns:
        bool: True if the simulated video file has horizontal drift compared to the original video file,
              False otherwise.
    """
    __print_test("Validating Horizontal Drift")
    try:
        # Open the original video file
        original_cap = cv2.VideoCapture(original_video_file)
        if not original_cap.isOpened():
            __print_failure("Error! Could not open original video file")
            return False

        # Open the simulated video file
        simulated_cap = cv2.VideoCapture(simulated_video_file)
        if not simulated_cap.isOpened():
            __print_failure("Error! Could not open simulated video file")
            return False

        original_x_list = []
        simulated_x_list = []

        # Calculate average brightness for a few frames of the original video
        while True:
            original_ret, original_frame = original_cap.read()
            if not original_ret:
                break
            original_x_list.append(original_frame.mean(axis=0).mean())
            if len(original_x_list) >= 100:  # Arbitrary number of frames to check
                break

        # Calculate average brightness for a few frames of the simulated video
        while True:
            simulated_ret, simulated_frame = simulated_cap.read()
            if not simulated_ret:
                break
            simulated_x_list.append(simulated_frame.mean(axis=0).mean())
            if len(simulated_x_list) >= 100:  # Arbitrary number of frames to check
                break

        original_avg_x = np.mean(original_x_list)
        simulated_avg_x = np.mean(simulated_x_list)

        if abs(simulated_avg_x - original_avg_x) < 5:
            __print_failure(
                f"Failed! Horizontal drift change is not significant. Original: {original_avg_x}, "
                "Simulated: {simulated_avg_x}"
            )
            return False

        __print_success(
            f"Success! Horizontal drift change is significant. Original: {original_avg_x}, "
            "Simulated: {simulated_avg_x}"
        )
        return True

    except Exception as e:
        __print_failure(f"Error during horizontal drift validation: {e}")
        return False


def validate_video_not_same(original_video_file, simulated_video_file):
    """
    Checks if the simulator produces a video that is different from the original video.
    Args:
        original_video_file (str): Path to the original video file.
        simulated_video_file (str): Path to the simulated video file.
    Returns:
        bool: True if the simulated video file is different from the original video file, False otherwise.
    """
    __print_test("Validating Video Not Same")
    try:
        # Open the original video file
        original_cap = cv2.VideoCapture(original_video_file)
        if not original_cap.isOpened():
            __print_failure("Error! Could not open original video file")
            return False

        # Open the simulated video file
        simulated_cap = cv2.VideoCapture(simulated_video_file)
        if not simulated_cap.isOpened():
            __print_failure("Error! Could not open simulated video file")
            return False

        # Check the file hash to see if the files are the same
        original_hash = hash(open(original_video_file, "rb").read())
        simulated_hash = hash(open(simulated_video_file, "rb").read())

        if original_hash == simulated_hash:
            __print_failure("Failed! Video files are the same.")
            return False

        # Check frame by frame if the two videos are the exact same
        while True:
            original_ret, original_frame = original_cap.read()
            simulated_ret, simulated_frame = simulated_cap.read()

            if not original_ret or not simulated_ret:
                break

            if not np.array_equal(original_frame, simulated_frame):
                __print_success("Success! Videos are different.")
                return True

        __print_success("Success! Videos are different.")
        return True
    except Exception as e:
        __print_failure(f"Error during video not same validation: {e}")
        return False


def validate_duration_same(original_video_file, simulated_video_file):
    __print_test("Validating Duration Same")
    video1 = cv2.VideoCapture(original_video_file)
    video2 = cv2.VideoCapture(simulated_video_file)

    duration1 = video1.get(cv2.CAP_PROP_FRAME_COUNT) / video1.get(cv2.CAP_PROP_FPS)
    duration2 = video2.get(cv2.CAP_PROP_FRAME_COUNT) / video2.get(cv2.CAP_PROP_FPS)

    video1.release()
    video2.release()

    if duration1 == duration2:
        __print_success("Success! Videos have the same duration.")
        return True
    __print_failure("Failed! Videos have different durations.")
    return False


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(
            "Usage: python check_simulation.py <original_video_file> <simulated_video_file>"
        )
        sys.exit(1)

    original_video_file = sys.argv[1]
    simulated_video_file = sys.argv[2]

    if not os.path.isfile(simulated_video_file):
        print(f"Error: The file {simulated_video_file} does not exist.")
        sys.exit(1)

    if not os.path.isfile(original_video_file):
        print(f"Error: The file {original_video_file} does not exist.")
        sys.exit(1)

    # Extract the simulation name from the file name
    file_name = os.path.basename(simulated_video_file)
    parts = file_name.split("_temp_")
    if len(parts) != 2:
        print(f"Error: The file name {file_name} is not in the expected format.")
        sys.exit(1)

    video_name = parts[0]
    simulation_name = parts[1].rsplit(".", 1)[0]

    error_count = 0
    failed_tests = []

    if simulation_name == "low_resolution":
        print("Found low resolution simulation. Validating...")
        if not validate_low_resolution(original_video_file, simulated_video_file):
            error_count += 1
            failed_tests.append("Low Resolution")
    elif simulation_name == "compression_artifacts":
        print("Found compression artifacts simulation. Validating...")
        if not validate_compression_artifacts(
            original_video_file, simulated_video_file
        ):
            error_count += 1
            failed_tests.append("Compression Artifacts")
    elif simulation_name == "brightness" or simulation_name == "dynamic_brightness":
        print("Found brightness simulation. Validating...")
        if not validate_change_brightness(original_video_file, simulated_video_file):
            error_count += 1
            failed_tests.append("Brightness")
    elif simulation_name == "simple_blur" or simulation_name == "complex_blur":
        print("Found blur simulation. Validating...")
        if not validate_blur(original_video_file, simulated_video_file):
            error_count += 1
            failed_tests.append("Blur")
    elif simulation_name == "contrast" or simulation_name == "dynamic_contrast":
        print("Found contrast simulation. Validating...")
        if not validate_contrast(original_video_file, simulated_video_file):
            error_count += 1
            failed_tests.append("Contrast")
    elif simulation_name == "noise":
        print("Found noise simulation. Validating...")
        if not validate_background_noise(original_video_file, simulated_video_file):
            error_count += 1
            failed_tests.append("Noise")
    elif simulation_name == "horizontal_drift":
        print("Found horizontal drift simulation. Validating...")
        if not validate_horizontal_drift(original_video_file, simulated_video_file):
            error_count += 1
            failed_tests.append("Horizontal Drift")

    if not validate_video_not_same(original_video_file, simulated_video_file):
        error_count += 1
        failed_tests.append("Video Not Same")
    if not validate_duration_same(original_video_file, simulated_video_file):
        error_count += 1
        failed_tests.append("Duration Same")

    if error_count == 0:
        __print_success("Success! All tests passed!")
    else:
        __print_failure(
            f"Failed! {error_count} tests failed: {', '.join(failed_tests)}"
        )
        sys.exit(1)
