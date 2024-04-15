#!/bin/bash
# Run the validator on all videos in the video folder
# $1 is the folder containing the videos, $2 is the simulation type
# Usage example: bash run-scripts/validation.sh videos normal

# Check if the required arguments are provided
if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: bash run-scripts/validation.sh <video_folder> <simulation_type>"
    exit 1
fi

# Start the python simulator process
python3 simulator.py $1 $2 &
PID=$!

# Give the simulator process some time to start
sleep 1

# Check if the python simulator process is still running
# If it is running, start the validator for each video in the folder
if ps -p $PID > /dev/null; then
    for video in "$1"/*; do
    (
        video="${video#videos/}"
        if [[ $video == *.mp4 || $video == *.ts ]]; then
            echo "Checking video: $video"
            python3 validator.py rtsp://localhost:8554/"$video"
        fi
    )
    done
else
    exit 1
fi

# Kill the simulator process
kill -2 $PID