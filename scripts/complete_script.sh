#!/bin/sh

# -------- User Input Section ----------
# Check if the user has provided the path to the videos folder
if [ -z "$1" ]; then
    echo "Please provide the path to the videos folder"
    exit 1
fi

# Check if the user has provided the simulation that they want to run
if [ -z "$2" ]; then
    echo "Please provide the simulation that you want to run"
    exit 1
fi

# Check if the user has provided the path to the original video
if [ -z "$3" ]; then
    echo "Please provide the path to the original video"
    exit 1
fi

# Check if the user has provided the path to the video logs
if [ -z "$4" ]; then
    echo "Please provide the path to the video logs"
    exit 1
fi

# Check if the user has provided the path to the OCR logs
if [ -z "$5" ]; then
    echo "Please provide the path to the OCR logs"
    exit 1
fi

# Check if the user has provided the path to the overlay image
if [ -z "$6" ]; then
    echo "Please provide the path to the overlay image"
    exit 1
fi

# Get the list of available simulations from the simulator
SIMULATIONS=$(python3 -u simulator/simulator.py | grep "Available simulations" | cut -d ":" -f 2)

# Save the user input in variables
VIDEOS_FOLDER=$1
SIMULATION=$2
ORIGINAL_VIDEO=$3
VIDEO_LOGS=$4
OCR_LOGS=$5
OVERLAY_IMAGE=$6

# Check if the simulation provided by the user is valid
if ! echo "$SIMULATIONS" | grep -q "$SIMULATION"; then
    echo "Invalid simulation. Available simulations are: $SIMULATIONS"
    exit 1
fi

# -------- Simulator Section ----------

# Start the simulator
python3 -u simulator/simulator.py $VIDEOS_FOLDER $SIMULATION > /tmp/simulator_pipe &
SIMULATOR_PID=$!

# Wait for the simulator to start
while true; do
    if grep -q "RTSP server running..." /tmp/simulator_pipe; then
        break
    fi
done

RTSP_URLS=$(grep "Stream available at" /tmp/simulator_pipe | cut -d " " -f 4)

# sleep 100
# kill -INT $SIMULATOR_PID
echo "RTSP server running..."

# -------- Video Processing Section ----------

# Check if the VD is running on the server
# If not, start the VD and wait for confirmation that it is running

# Send curl to start recording
# Sleep for duration to continue recording
# Send curl to stop recording

# Extract the videos from the VD with scp
# Save the result videos in the folder called video_folder in the current directory
# Save the ocr logs in the folder called ocr_logs in the current directory
# Save the video logs in the folder called video_logs in the current directory
# Save the overlay image as overlay_image.jpg in the current directory


# -------- Validator Section ----------

python3 validator/validator.py $VIDEOS_FOLDER $VIDEO_LOGS $OCR_LOGS $OVERLAY_IMAGE 0

# -------- Cleanup Section ----------

# Kill the simulator
kill -INT $SIMULATOR_PID

# Delete the pipes
rm /tmp/simulator_pipe