from module.sequence import *
from json import dump
from tkinter import filedialog
import os
import pickle

class FileHandler:
    class ID:
        POSE = 0
        MOTOR = 1
        PATH = 2
        FLAG = 3
        WAIT = 4
        PNEU = 5
        CUSTOM = 6
    
    def __init__(self):
        self.file_path: None | str
        with open(r"persistent.json") as f:
            self.file_path = load(f)['last_edited_path']
        
        self.path_exists = os.path.exists(self.file_path)
        self.base_name = os.path.basename(self.file_path)

        self.save_data = []

    def save_as(self, sequence: list[SequenceType]):
        self.file_path = filedialog.asksaveasfilename(defaultextension=".autopath", filetypes=[("Auto Path Files", "*.autopath"), ("All Files", "*.*")])
        if self.file_path == '':
            self.file_path = None
        else:
            self.base_name = os.path.basename(self.file_path)
            self.save(sequence)
    
    def save(self, sequence: list[SequenceType]):
        if self.file_path is None:
            self.save_as(sequence)
            return
        
        # if we cancelled the dialog
        if self.file_path is None:
            return
        
        with open(self.file_path, 'wb') as f:
            pickle.dump(sequence, f)

        print(f"Saved {self.file_path}: {os.path.getsize(self.file_path)}b")

        with open(r"persistent.json") as f:
            l = load(f)
        
        with open(r"persistent.json", 'w') as f:
            l["last_edited_path"] = self.file_path
            dump(l, f, indent=1)

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
                # format events for export
                events = []
                for event in function.events:
                    args = {}
                    if event['name'] == 'set_flag':
                        # with flags we don't want to export the arg if it is the same as the default flag, so only if we have changed something
                        #! this could interfere if the default in the set_flag.json file is the same as what we want to set it to
                        # but i'm too lazy to fix rn, and if we export all the flags it makes events really big *shrug*
                        with open(rf"settings\events\{event['name']}.json") as f:
                            reference_data = load(f)
                        
                        # check each argument in the event
                        for arg in event['data']['arguments']:
                            # see if it is different then the same argument in the reference file
                            if event['data']['arguments'][arg] != reference_data['arguments'][arg]:
                                args[arg] = event['data']['arguments'][arg]
                    else:
                        args = event['data']['arguments']

                    for arg in args:
                        if type(args[arg]) == dict:
                            args[arg] = args[arg]['default']
                    events.append((event['name'], args, event['pos']))
                    
                item = [FileHandler.ID.PATH, 
                        events,
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
            elif isinstance(function, SequenceCuston):
                item = [
                    FileHandler.ID.CUSTOM,
                    function.ID
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

    def load(self, filepath: str | None = None) -> list[SequenceType] | None:
        """
        Load data from a .autopath file into a sequence list. 
        """
        if filepath is None:
            filepath = filedialog.askopenfilename(filetypes=[("Autopath files", "*.autopath")])

        if os.path.exists(filepath):
            print(f"Loaded {filepath}")
            self.file_path = filepath
            self.base_name = os.path.basename(self.file_path)
            with open(filepath, 'rb') as f:
                try:
                    return pickle.load(f)
                except AttributeError:
                    print("Couldn't find attribute. This likely means that the file is outdated and has old code.")
                    return None
        else:
            print(f"File not found: {filepath}")
            return None
    
    def load_most_recent(self):
        with open(r"persistent.json") as f:
            self.file_path = load(f)['last_edited_path']
        self.path_exists = os.path.exists(self.file_path)
        self.base_name = os.path.basename(self.file_path)

        return self.load(self.file_path)
