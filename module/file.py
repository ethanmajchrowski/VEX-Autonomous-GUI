from module.sequence import *
from tkinter import filedialog
import os

class FileHandler:
    class ID:
        POSE = 0
        MOTOR = 1
        PATH = 2
        FLAG = 3
        WAIT = 4
        PNEU = 5
    
    def __init__(self):
        self.file_path: None | str = None
        self.file_path = "C:/Users/ethan/projects/Python/Autonomous GUI/save_testing/main.autopath"
        self.save_data = []

    def save_as(self, sequence: list[SequenceType]):
        self.file_path = filedialog.asksaveasfilename(defaultextension=".autopath", filetypes=[("Auto Path Files", "*.autopath"), ("All Files", "*.*")])
        if self.file_path == '':
            self.file_path = None
        else:
            self.save(sequence)
    
    def save(self, sequence: list[SequenceType]):
        if self.file_path is None:
            self.save_as(sequence)
            return
        
        # if we cancelled the dialog
        if self.file_path is None:
            return
        
        with open(self.file_path, 'w') as f:
            f.write(str(self.save_lossless(sequence)))

        print(f"Saved {self.file_path}: {os.path.getsize(self.file_path)}b")

    def save_lossless(self, sequence: list[SequenceType]) -> list:
        """
        Export needed data to restore work in the future.
        """
        output = []
        item = []
        for function in sequence:
            if isinstance(function, SequenceDriveFor):
                pass
            elif isinstance(function, SequenceFlag):
                args = []
                for item in function.custom_args:
                    args.append((item, function.custom_args[item]['value'][1]))
                item = [
                    FileHandler.ID.FLAG,
                    args
                ]
            elif isinstance(function, SequenceMotor):
                pass
            elif isinstance(function, SequencePath):
                item = [FileHandler.ID.PATH, 
                        None, # events
                        function.custom_args, 
                        [curve.control_points for curve in function.curve.curves], 
                        function.curve.overlap_points,
                        function.curve.spacing]
            elif isinstance(function, SequenceTurnFor):
                pass
            elif isinstance(function, SequenceInitialPose):
                item = [
                    FileHandler.ID.POSE,
                    [function.x, function.y],
                    function.a
                ]

            output.append(item)
        
        return output

    # Handle exporting and importing data files
    def export_lossy(self, sequence: list[SequenceType]) -> list:
        """
        Exports to list that can be put on a robot. Gets path points, functions & custom arguments, etc.
        Final format: 
        [
            ['path', events, checkpoints, custom_args, points],
            ['motor', motor, direction, speed, speed_type],
            ['flag', name, value],
            ['turn_for', direction, degrees, speed, timeout, custom_args],
            ['drive_for', direction, dist, speed, timeout, custom_args]
        ]
        """
        self.save(sequence)
        print("\nExporting...")

        output = []
        error = False
        for i, function in enumerate(sequence):
            item = None
            
            if isinstance(function, SequenceDriveFor):
                pass
            elif isinstance(function, SequenceFlag):
                args = tuple([(item, function.custom_args[item]['value'][1]) for item in function.custom_args
                               if not function.custom_args[item]['value'][1] == function.format['arguments'][item]['value'][1]])
                if args:
                    item = [
                        FileHandler.ID.FLAG,
                        args
                    ]
                else:
                    print(f"Export INFO: Attempted to export flag event, was empty (Sequence index {i})")
                    error = True

            elif isinstance(function, SequenceMotor):
                # Exports motor in one of two ways:
                # 1. Spin:
                #       use voltage or velocity as speed (index 3)
                #       use direction as -1 (backwards) or 1 (forwards) (index 2)
                #       use motor as motor (index 1)
                # 2. Stop:
                #       use direction as 0 (index 2)
                #       use braketype as braketype (index 3)
                #       use motor as motor (index 1)
                #   ['motor', 'leftC', 0, 'COAST']
                if function.properties['motor'][2] is None:
                    print(f"Export WARN: Cannot export motor None (Sequence index {i})")
                    error = True
                elif ('braketype' not in function.custom_args) and ('voltage' not in function.custom_args and 'velocity' not in function.custom_args):
                    print(f"Export ERROR: Motor has no braketype or velocity (Sequence index {i})")
                    error = True
                else:
                    speed = 0
                    if 'direction' in function.custom_args:
                        direction = function.custom_args['direction']['value'][1]
                    if 'voltage' in function.custom_args and direction:
                        speed = function.custom_args['voltage']['value'][1]
                    elif 'velocity' in function.custom_args and direction:
                        speed = function.custom_args['velocity']['value'][1]
                        # convert velocity to speed
                        speed = round((speed / 100) * 12.0, 2)
                    else:
                        if 'braketype' in function.custom_args:
                            speed = function.custom_args['braketype']['value'][1]
                            direction = 0
                        
                    item = [FileHandler.ID.MOTOR, function.properties['motor'][2], direction, speed]

            elif isinstance(function, SequencePath):
                if function.custom_args['fwd_volt']['value'][1] == 0.0:
                    print(f"Export WARN: Path has forward speed of 0.0 volts (Sequence index {i})")
                    error = True
                item = [FileHandler.ID.PATH, 
                        None, # events
                        tuple([(item, function.custom_args[item]['value'][1]) for item in function.custom_args
                               if not function.custom_args[item]['value'][1] == function.format['arguments'][item]['value'][1]]), 
                        function.curve.get_points()]
            elif isinstance(function, SequenceTurnFor):
                pass
            elif isinstance(function, SequenceInitialPose):
                item = [
                    FileHandler.ID.POSE,
                    {
                        "pos": [function.x, function.y],
                        "angle": function.a
                    }
                ]
            elif isinstance(function, SequenceSleepFor):
                if function.t == 0:
                    print(f"Export WARN: Sleep has time 0 (Sequence index {i})")
                    error = True

                else:
                    item = [
                        FileHandler.ID.WAIT,
                        function.t
                    ]
            elif isinstance(function, SequenceSetPneumatic):
                if function.properties['pneumatic'][2] is None:
                    print(f"Export WARN: Cannot export pneumatic None (Sequence index {i})")
                    error = True
                else:
                    item = [
                        FileHandler.ID.PNEU,
                        function.state,
                        function.properties['pneumatic'][2]
                    ]
            else:
                item = None

            if item is not None:
                output.append(item)

        if not error:
            print("No export errors detected!")

        fp = self.file_path.strip(".autopath") + ".txt"
        with open(fp, 'w') as f:
            # f.write(str(output).replace(" ", ""))
            f.write("[\n")
            for line in output:
                f.write(str(line) + ",\n")
            f.write("]\n")
        print(f"Exported to {fp}: {os.path.getsize(fp)}b")

        return output

    def load(self, filepath: str) -> list[SequenceType]:
        """
        Load data from a .autopath file into a sequence list. 
        """
