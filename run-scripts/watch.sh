#!/bin/bash
# Start ffplay for each video in the specified folder
# $1 is the folder containing the videos, $2 is the simulation type
# To get verbose output, use the -v flag
# Usage example: bash run-scripts/watch.sh -v videos normal

# Initialize verbose flag
verbose=0

# Parse command-line options for a verbose flag
while getopts ":v" opt; do
  case ${opt} in
    v )
      verbose=1 ;;
    \? )
      echo "Invalid option: $OPTARG" 1>&2
      ;;
  esac
done
shift $((OPTIND -1))

# Check if the required arguments are provided
if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: bash run-scripts/watch.sh [-v] <video_folder> <simulation_type>"
    exit 1
fi

# Start the python simulator process
python3 simulator.py "$1" "$2" &
PID=$!

# Give the simulator process some time to start
sleep 1

# Declare an array to hold FFPLAY PIDs
FFPLAY_PIDs=()

# Check if the python simulator process is still running
# If it is running, start ffplay for each video in the folder
# and store the PIDs in the FFPLAY_PIDs array
if ps -p $PID > /dev/null; then
    for video in "$1"/*; do
        echo "Playing video: rtsp://localhost:8554/${video#*/}"
        if [ "$verbose" -eq 1 ]; then
            ffplay rtsp://localhost:8554/"${video#*/}" &
        else
            ffplay rtsp://localhost:8554/"${video#*/}" > /dev/null 2>&1 &
        fi
        FFPLAY_PID=$!
        FFPLAY_PIDs+=("$FFPLAY_PID")
    done
else
    exit 1
fi

# Wait for all ffplay processes to complete
for PIDFF in "${FFPLAY_PIDs[@]}"; do
    wait "$PIDFF"
done

# Kill the simulator process
kill -2 $PID
