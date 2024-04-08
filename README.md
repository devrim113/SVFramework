# Validation Framework

## Description
This is a Simulation and Validation framework for RTSP streams. The goal of the project is to simulate RTSP streams most commonly used by IP cameras to transport video. The simulator performs operations on the simulated stream to simulate errors, failures and problems with the stream. The system should keep operating and sometimes even fix these mistakes. The validation part checks the stream and checks if the error, failures and problems are solved or not.

## Installation
To setup the parts clone this project and run the following commands:

xargs sudo apt-get install -y < apt-get-requirements.txt
pip install -r requirements.txt

## Usage
The program can be run using the run-scripts, which each are documented seperately.
The main usage is as follows:

For the simulator:

python3 simulator.py <video_folder> <simulation>

With the possible simulations being all the methods in simulations.py

For the validator:

python3 validator.py <streaming_url>
