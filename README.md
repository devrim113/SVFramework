# Simualtion and Validation Framework

## Overview

The Simulation and Validation Framework is a comprehensive tool designed to validate and simulate videos recorded through RTSP streams and IP camera's for robust testing. This project contains scripts, simulators, and validators necessary for creating a consistent validation workflow.

## Project Structure

The project is organized into the following directories and key files:

- `.github/`: Contains GitHub-related configurations and workflows.
- `.gitignore`: Specifies files and directories to be ignored by Git.
- `README.md`: This file, which provides an overview and instructions for the project.
- `apt-get-requirements.txt`: List of system packages required to run the project.
- `framework_validation/`: Contains validation frameworks.
  - `simulator/`: Includes simulator-related code.
- `requirements.txt`: List of Python packages required to run the project.
- `scripts/`: Contains scripts to execute various tasks.
  - `complete_script.sh`: A script to run the complete validation and simulation process.
  - `sim_result.sh`: A script to handle simulation results.
  - `val_result.sh`: A script to handle validation results.
- `simulator/`: Contains the simulation logic.
  - `config.py`: Configuration settings for the simulator.
  - `simulations.py`: Simulation scenarios and their definitions.
  - `simulator.py`: Main simulator execution script.
- `validator/`: Contains the validation logic.
  - `validations.py`: Validation scenarios and their definitions.
  - `validator.py`: Main validator execution script.

## Installation

To set up the project, follow these steps:

1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/ValidationFramework.git
   cd ValidationFramework
   ```

2. **Install system dependencies**
    ```sh
    sudo apt-get update
    sudo apt-get install -y $(cat apt-get-requirements.txt)
    ```

3. **Install Python dependencies**
    ```sh
    pip install -r requirements.txt
    ```

## Usage

### Running Simulations

To run the simulations, use the following command:

```sh
python simulator/simulator.py <video_folder> <simulation_type>
```

### Running Validations

To run the validations, use the following command:

```sh
python validator/validator.py <video_folder> <video_logs_folder> <ocr_logs_folder> <overlay_image> <vmaf_option>
```

### Complete Simulation and Validation Proces

To execute the complete simulation and validation process in your own pipeline, update and run the provided shell script:

```sh
sh scripts/complete_script.sh
```
