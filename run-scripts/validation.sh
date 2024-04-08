#!/bin/bash
# Run the validator on all videos in the videos directory

for video in videos/*; do
    (
        video="${video#videos/}"
        printf "Checking video: $video\n"
        python3 validator.py rtsp://localhost:8554/"$video"
    )
done

wait