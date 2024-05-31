import hashlib
import cv2
import imagehash
from PIL import Image


def get_file_hash(file_path):
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()


def get_video_metadata(file_path):
    video = cv2.VideoCapture(file_path)
    metadata = {
        "frame_count": int(video.get(cv2.CAP_PROP_FRAME_COUNT)),
        "fps": video.get(cv2.CAP_PROP_FPS),
        "width": int(video.get(cv2.CAP_PROP_FRAME_WIDTH)),
        "height": int(video.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        "duration": int(
            video.get(cv2.CAP_PROP_FRAME_COUNT) / video.get(cv2.CAP_PROP_FPS)
        ),
    }
    video.release()
    return metadata


def are_videos_similar(file1, file2, threshold=0.95):
    video1 = cv2.VideoCapture(file1)
    video2 = cv2.VideoCapture(file2)

    while True:
        ret1, frame1 = video1.read()
        ret2, frame2 = video2.read()

        if not ret1 or not ret2:
            break

        hash1 = imagehash.average_hash(
            Image.fromarray(cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB))
        )
        hash2 = imagehash.average_hash(
            Image.fromarray(cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB))
        )

        similarity = 1 - (hash1 - hash2) / len(hash1.hash) ** 2
        if similarity < threshold:
            return False

    video1.release()
    video2.release()
    return True


def __print_success(message):
    print(f"\033[32m{message}\033[0m")


def __print_failure(message):
    print(f"\033[31m{message}\033[0m")


def __print_test(message):
    width = 60
    dot_count = width - len(message)
    print(f"{message}{'.' * max(dot_count, 1)}", end="", flush=True)


def main(original_video, manipulated_video):
    # Test 1: File Hash Comparison
    __print_test("Comparing file hashes")
    original_hash = get_file_hash(original_video)
    manipulated_hash = get_file_hash(manipulated_video)
    if original_hash == manipulated_hash:
        __print_success("Success! The files are identical.")
    else:
        __print_failure("Failure! The files are different.")

    # Test 2: Metadata Comparison
    __print_test("Comparing video metadata")
    original_metadata = get_video_metadata(original_video)
    manipulated_metadata = get_video_metadata(manipulated_video)
    if original_metadata == manipulated_metadata:
        __print_success("Success! The metadata is identical.")
    else:
        __print_failure("Failure! The metadata is different.")

    # Test 3: Frame-by-Frame Comparison
    __print_test("Comparing video frames")
    if are_videos_similar(original_video, manipulated_video):
        __print_success("Success! The videos are similar.")
    else:
        __print_failure("Failure! The videos are different.")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python compare_videos.py <original_video> <manipulated_video>")
        sys.exit(1)

    original_video = sys.argv[1]
    manipulated_video = sys.argv[2]

    main(original_video, manipulated_video)
