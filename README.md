# Validation Framework

## Description
This is a Simulation and Validation framework for RTSP streams. The goal of the project is to simulate RTSP streams most commonly used by IP cameras to transport video. The simulator performs operations on the simulated stream to simulate errors, failures and problems with the stream. The system should keep operating and sometimes even fix these mistakes. The validation part checks the stream and checks if the error, failures and problems are solved or not.

For the project, we use python files that call gstreamer and ffmpeg functionalities.

## Installation
To setup the parts clone this project and run the following commands:

`xargs sudo apt-get install -y < apt-get-requirements.txt`

`pip install -r requirements.txt`

## Usage
The program can be run using the run-scripts. There are two main scripts to use:

`bash run-scripts/validation.sh <video_folder> <simulation>`

This fires up the simulator with the video folder and the simulation and immediatly calls the validator with the correct url's. All the output is returned to the user.

`bash run-scripts/watch.sh [-v] <video_folder> <simulation>`

Fires up the simulator with the video folder and the simulation and starts a ffplay watch window for each stream. The optional -v verbose flag gives the output of ffplay to the user.

The main usage is as follows:

For the simulator:

`python3 simulator.py <video_folder> <simulation>`

With the possible simulations being all the methods in simulations.py and the video folder being the place where you stored the videos you want to stream. The simulator will run a stream for each video you put in this folder.

For the validator:

`python3 validator.py <streaming_url>`

With the streaming url being the url you want to validate.
