#!/bin/bash

# Array of simulation types
simulation_types=(
    "low_resolution" "compression_artifacts" "change_brightness" "dynamic_change_brightness"
    "simple_blur" "change_contrast" "dynamic_change_contrast"
    "background_noise" "horizontal_drift"
)

# Array of video folders (under simulator_benchmark)
video_folders=(
    "video_10s_mp4" "video_1m_mp4" "video_10m_mp4" "video_30m_mp4" "video_2h_mp4"
    "video_10s_ts" "video_1m_ts" "video_10m_ts" "video_30m_ts" "video_2h_ts"
)

# Base directory for video folders and logs
base_dir="simulator_benchmark"
log_dir="$base_dir/logs"

# Ensure the log directory exists
mkdir -p $log_dir

# Function to calculate the duration of the video (assumes one video file in the folder)
get_video_duration() {
    local video_folder=$1
    local video_file=$(ls $video_folder | head -n 1)
    local duration=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$video_folder/$video_file")
    echo $duration
}

# Function to run a simulation and measure its runtime
run_simulation() {
    local sim_type=$1
    local video_folder=$2
    local log_file=$3

    echo "Starting simulation: $sim_type" | tee -a $log_file

    total_time=0
    total_speedup=0

    for iteration in {1..5}; do
        echo "Iteration $iteration for $sim_type" | tee -a $log_file

        # Remove the test_pipe if it exists and create a new one
        rm -f /tmp/test_pipe
        touch /tmp/test_pipe

        # Record the start time
        start_time=$(date +%s%N)

        # Start the simulator in the background
        python3 -u simulator/simulator.py "$video_folder" "$sim_type" > /tmp/test_pipe &
        SIMULATOR_PID=$!

        # Wait for the simulation to complete by scanning the pipe
        while true; do
            if grep -q "RTSP server running..." /tmp/test_pipe; then
                break
            fi
        done

        # Record the end time
        end_time=$(date +%s%N)

        # Calculate the elapsed time in seconds with nanosecond precision
        elapsed_time=$(echo "scale=3; ($end_time - $start_time) / 1000000000" | bc)

        # Calculate the speedup
        speedup=$(echo "scale=3; $video_duration / $elapsed_time" | bc)

        # Accumulate the total time and speedup
        total_time=$(echo "$total_time + $elapsed_time" | bc)
        total_speedup=$(echo "$total_speedup + $speedup" | bc)

        # Print detailed iteration results to the log file
        echo "Iteration $iteration results for $sim_type" >> $log_file
        echo "Elapsed time: $elapsed_time seconds" >> $log_file
        echo "Speedup: $speedup" >> $log_file
        echo "---------------------------------" >> $log_file

        # Clean up
        kill -INT $SIMULATOR_PID
        rm -f /tmp/test_pipe
        sleep 2
    done

    # Calculate the average time and speedup
    average_time=$(echo "scale=3; $total_time / 5" | bc)
    average_speedup=$(echo "scale=3; $total_speedup / 5" | bc)

    # Print the results
    echo "Simulation type: $sim_type" | tee -a $log_file
    echo "Average elapsed time: $average_time seconds" | tee -a $log_file
    echo "Average speedup: $average_speedup" | tee -a $log_file
    echo "---------------------------------" | tee -a $log_file
    echo "$sim_type ($average_time""s/$average_speedup""x)" | tee -a $log_file
    echo "---------------------------------" | tee -a $log_file
}

# Run simulations for each video folder
for video_folder in "${video_folders[@]}"; do
    folder_path="$base_dir/$video_folder"

    # Get the duration of the video
    video_duration=$(get_video_duration $folder_path)

    if [ -z "$video_duration" ]; then
        echo "Failed to get the video duration for $video_folder. Ensure there's a video file in the folder."
        continue
    fi

    echo "Video duration for $video_folder: $video_duration seconds"

    # Create or clear the log file for the current video folder
    log_file="$log_dir/${video_folder}_simulation_output.log"
    > $log_file

    # Run each simulation type and measure runtime
    for sim_type in "${simulation_types[@]}"; do
        run_simulation "$sim_type" "$folder_path" "$log_file"
    done

    echo "All simulations for $video_folder completed." | tee -a $log_file
done

echo "All simulations for all video folders completed."
