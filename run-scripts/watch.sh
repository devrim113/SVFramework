#!/bin/bash
# Start ffplay for each video in the videos directory

for video in videos/*; do
    (
        video="${video#videos/}"
        ffplay rtsp://localhost:8554/"$video"
    ) &
done

wait