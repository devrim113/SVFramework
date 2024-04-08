#!/bin/bash

for video in videos/*; do
    (
        video="${video#videos/}"
        ffplay rtsp://localhost:8554/"$video"
    ) &
done

wait