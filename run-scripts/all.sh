#! /bin/bash
# Run the simulator in normal mode and run the validator on all videos in the videos directory
# Perform the validation immediately after starting the simulator

python3 simulator.py videos normal &
PID=$!
sleep 2
sh run-scripts/validation.sh
kill -2 $PID