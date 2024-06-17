# Array of video folders (under simulator_benchmark)
video_folders=(
    "video_10s_mp4" "video_1m_mp4" "video_10m_mp4" "video_30m_mp4" "video_2h_mp4"
)

# Base directory for video folders and logs
base_dir="simulator_benchmark"
log_dir="$base_dir/logs_val"

# Ensure the log directory exists
mkdir -p $log_dir

# Function to calculate the duration of the video (assumes one video file in the folder)
get_video_duration() {
    local video_folder=$1
    local video_file=$(ls $video_folder | head -n 1)
    local duration=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$video_folder/$video_file")
    echo $duration
}

# Function to run the validator and measure its runtime
run_validation() {
    local video_folder=$1
    local video_logs=$2
    local ocr_logs=$3
    local overlay_image="overlay_image.png"
    local vmaf_option="1"
    local log_file=$4

    echo "Starting validation for $video_folder" | tee -a $log_file

    total_time=0
    total_speedup=0

    for iteration in {1..1}; do
        echo "Iteration $iteration for $video_folder" | tee -a $log_file

        # Run the validator and capture the total time
        ouptut=$(python3 validator/validator.py "$video_folder" "$video_logs" "$ocr_logs" "$overlay_image" "$vmaf_option" | tee -a $log_file)
        while true; do
            if grep -q "Total test duration:" $log_file; then
                total_time=$(grep -oP 'Total test duration: \K[\d.]+' $log_file)
                break
            fi
        done
        # total_time=$(python3 validator/validator.py "$video_folder" "$ocr_logs" "$overlay_image" "$vmaf_option" | grep -oP 'Total test duration: \K[\d.]+')

        echo "Total time for $video_folder: $total_time seconds" | tee -a $log_file
    done

    # Calculate the average time and speedup
    # avg_time=$(echo "scale=3; $total_time / 1" | bc)
    # echo "Average time for $video_folder: $avg_time seconds" | tee -a $log_file
    # average_speedup=$(echo "scale=3; $total_time / $video_duration" | bc)
    # echo "Average speedup for $video_folder: $average_speedup" | tee -a $log_file
}

# Iterate over each video folder and run the validation
for video_folder in "${video_folders[@]}"; do
    log_file="$log_dir/${video_folder}_validation_output.log"
    video_duration=$(get_video_duration "simulator_benchmark/$video_folder")
    video_logs="video_logs/"
    ocr_logs="ocr_logs/"
    run_validation "simulator_benchmark/$video_folder" "$video_logs" "$ocr_logs" "$log_file"
done