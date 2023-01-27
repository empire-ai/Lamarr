# Lamarr
Python toolset to provide simple to use functionalty to record and use desktop and robotics macros as jupyter lab workbooks

## Description
Lamarr is a set of scripts in single Jupyter-Lab worksheet, to allow remotly run and maintain corporate/manufacturing processes

### Step
Each step is an image that automation script will try to locate on screen, if sucessfull or not it will launch a script that will choose next action or stop the script and wait for user interaction.
Step contains primary pattern and secondary pattern (max distance, found/not_found)
Script pyton code to be ran after detection

Before creating a new step double check that the step does not exist, if current are is dedecten among other split the closest one with chaning the seondary pattern

### Workflow
A set of steps to achive single goal. Will allow to 'pause' the state untill user interaction.
Each workflow is unique Jupyter lab worksheet, once ran the output is saved

### Robot


# Usage
pip install empire-lamarr

Here is sample how to select some text in the jupyter editor and copy print this text in python
Here is a demo:
<make a video here>


