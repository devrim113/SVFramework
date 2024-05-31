import os
import sys
import subprocess

def reverse_brightness(video_file):
    """
    Reverse brightness change by applying the inverse brightness adjustment.
    Args:
        video_file (str): The manipulated video file to process.
    Returns:
        str: The path to the brightness-reversed video.
    """
    # Placeholder value for brightness factor; in practice, this should be derived or passed
    brightness_factor = 0.35  # Example value; replace with actual factor used in manipulation

    # Calculate the reversed brightness factor
    reversed_brightness_factor = -brightness_factor

    # Generate the output file name
    output_video = video_file.rsplit(".", 1)[0] + "_reversed." + video_file.rsplit(".", 1)[1]

    # FFmpeg command to reverse the brightness adjustment
    command = [
        "ffmpeg", "-i", video_file, "-vf", f"eq=brightness={reversed_brightness_factor}", output_video, "-y"
    ]

    # Run the command and capture the output
    subprocess.run(command, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

    print(f"Reversed brightness video file created: {output_video}")
    return output_video

if __name__ == "__main__":
    # Define available simulation types
    simulation_types = ["brightness"]

    # Get the simulation type and manipulated video file from the command line arguments
    if len(sys.argv) == 3:
        manipulated_video = sys.argv[1]
        simulation_type = sys.argv[2]

        # Check if the manipulated video file exists
        if not os.path.exists(manipulated_video):
            print(f"The manipulated video file '{manipulated_video}' does not exist.")
            sys.exit(1)

        # Reverse the simulation
        if simulation_type in simulation_types:
            if simulation_type == "brightness":
                reversed_video = reverse_brightness(manipulated_video)
            else:
                print(f"No reversal defined for simulation type: {simulation_type}")
                sys.exit(1)
        else:
            print("Invalid simulation type. Please specify a valid simulation.")
            print("Usage: python reverse_simulation.py <manipulated_video> <simulation_type>")
            print("Available simulations: " + ", ".join(simulation_types))
            sys.exit(1)
    else:
        print("Please specify a manipulated video and a simulation type to reverse.")
        print("Usage: python reverse_simulation.py <manipulated_video> <simulation_type>")
        print("Available simulations: " + ", ".join(simulation_types))
        sys.exit(1)
