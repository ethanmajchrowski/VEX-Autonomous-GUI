**VEX Autonomous GUI**
# Overview
This project is a graphical tool designed to simplify the development and iteration of autonomous routines for VEX robotics. It was created to address a recurring pain point in our workflow: autonomous code was difficult to visualize, modify, and debug when written entirely by hand.

The GUI provides a structured way to build, edit, and reorder autonomous “events,” making it faster and less error-prone to develop complex autonomous sequences during competition preparation.

# Motivation
Developing autonomous routines directly in code made rapid iteration difficult, especially when testing different strategies or tuning parameters with limited time.

This tool was built as a practical solution to that problem: a way to abstract autonomous actions into configurable events that could be assembled visually while still producing robot-readable output.

# How it Works
* Autonomous sequences are composed of discrete events, defined as classes in module/sequence.py.
* Each event exposes its configurable arguments via JSON definitions located in settings/output/ (to support easy configurations for different robot codebases).
* The GUI dynamically interprets these definitions, allowing event parameters to be added, modified, and reordered interactively.
* The final autonomous routine is exported using the format defined in module/file.py, currently as a Python list of events.
* On the robot, these events are executed sequentially to perform the autonomous routine.

# Impact & Use
In practice, this tool significantly reduced the time required to create and adjust autonomous routines. It allowed for quicker experimentation, clearer visualization, and fewer errors. While the GUI itself is an MVP, the underlying approach proved effective and was actively used during competition.

# GUI Screenshot
![image](https://github.com/user-attachments/assets/a4841e62-55d8-41e8-83c2-6da55ecfb57b)
requirements.txt does not exist right now but ill get around to it
