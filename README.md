**VEX Autonomous GUI**

so this code sucks but this is a MVP of a gui program designed for VEX

essentially the sequence pulls from the classes defined in module/sequence.py, where they pull argument format from JSON located in settings/output/. Those are interpreted by the program to be added and changed in arguments/properties of that sequence event. Output format is defined in module/file.py and currently is just a python list of 'events' interpreted by our robot one at a time.
