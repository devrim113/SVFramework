#!/bin/bash

for video in videos/*; do
    (
        video="${video#videos/}"
        printf "Checking video: $video\n"
        python3 validation.py rtsp://localhost:8554/"$video"
    )
done

wait