from json import load
from copy import deepcopy

class SequenceType:
    def __init__(self, name: str):
        self.properties: dict = {
            "name": name  
            # all other formats are [obj, name, value]
        }
        self.format: dict
        self.custom_args = {}
        self.symbol: str

def load_format(fp: str):
    """
    Parses argument format from output format file to python dictionary.
    Outputs into 
    {
        "arguments": {
            # simple argument
            "name": [type, default_value],

            # complex argument
            "name": {
                "value": [type, default_value],
                "incompatible_with": ["name"],
                ...
            }
        }
    }
    Example sequence data
    {
        'arguments': {
            'backwards': {'value': [<class 'bool'>, False]}, 
            'look_ahead_dist': {'value': [<class 'int'>, 350]}, 
            'finish_margin': {'value': [<class 'int'>, 100]}, 
            'event_look_ahead_dist': {'value': [<class 'int'>, 75]}, 
            'timeout': {'value': [<class 'int'>, None]} 
            ...
        }
    }
    """
    with open(fp) as f:
        data = load(f)
    for arg_key in data['arguments']:
        # Complex arguments
        argument_type = type(data['arguments'][arg_key])
        if argument_type == dict:
            argument = data['arguments'][arg_key]
            data['arguments'][arg_key] = {}

            # add custom arguments to output
            if "default" in argument and "type_ref" in argument:
                data['arguments'][arg_key]["value"] = [type(argument["type_ref"]), argument["default"]]

                if type(argument["type_ref"]) == list:
                    data['arguments'][arg_key]["value"] = [(type(argument["type_ref"][0]), type(argument["type_ref"][1])), argument["default"]]
            elif "default" in argument:
                data['arguments'][arg_key]["value"] = [type(argument["default"]), argument["default"]]
            if "incompatible_with" in argument:
                data['arguments'][arg_key]["incompatible_with"] = argument["incompatible_with"]
            if "valid_types" in argument:

                data['arguments'][arg_key]["valid_types"] = argument["valid_types"]

        else:
            data['arguments'][arg_key] = {"value": [type(data['arguments'][arg_key]), data['arguments'][arg_key]]}
        
    return data

from module.curves import ComplexCurve
class SequencePath(SequenceType):
    def __init__(self, name: str = "Path", spacing = 50):
        super().__init__(name)
        self.symbol = "P"
        self.curve = ComplexCurve(control_points = [[[0, 0], [0, 600]], [[600, 600], [600, 0]]])

        self.format = load_format(r"settings\output\path.json")

        self.properties["point_spacing"] = ["value", self.curve, "spacing", spacing]
        self.custom_args["fwd_volt"] = deepcopy(self.format["arguments"]["fwd_volt"])
        self.events = [{'type': 'variable', 'name': 'fwd_speed', 'value': 2.0}, {'type': 'function', 'name': 'spin', 'args': [100, 'PERCENT'], 'obj': 'motor.intakeChain'}]

class SequenceMotor(SequenceType):
    def __init__(self, name: str = "Motor"):
        super().__init__(name)
        self.symbol = "M"

        self.format = load_format(r"settings\output\motor.json")

        self.properties["motor"] = ["list", self.format["motors"], None]
        self.custom_args["direction"] = deepcopy(self.format["arguments"]["direction"])
        self.custom_args["velocity"] = deepcopy(self.format["arguments"]["velocity"])

class SequenceFlag(SequenceType):
    def __init__(self, name: str = "Flag"):
        super().__init__(name)
        self.symbol = "F"

        self.format = load_format(r"settings\output\flag.json")

class SequenceTurnFor(SequenceType):
    def __init__(self, name: str = "TurnFor"):
        super().__init__(name)
        self.symbol = "T"

class SequenceDriveFor(SequenceType):
    def __init__(self, name: str = "DriveFor"):
        super().__init__(name)
        self.symbol = "D"

class SequenceInitialPose(SequenceType):
    def __init__(self, name: str = "InitialPose"):
        super().__init__(name)
        self.symbol = "START"

        self.format = {"arguments": {}}
        self.x, self.y, self.a = 0, 0, 0
        self.properties["x"] = ["value", self, "x", 0]
        self.properties["y"] = ["value", self, "y", 0]
        self.properties["theta"] = ["value", self, "a", 0]

class SequenceSleepFor(SequenceType):
    def __init__(self, name: str = "WaitFor"):
        super().__init__(name)
        self.symbol = "W"

        self.format = {"arguments": {}}
        self.t = 0
        self.properties["t"] = ["value", self, "t", 0]

class SequenceSetPneumatic(SequenceType):
    def __init__(self, name: str = "SetPneumatic"):
        super().__init__(name)
        self.symbol = "PNEU"

        self.format = load_format(r"settings\output\pneumatic.json")
        self.state = False
        self.properties["state"] = ["value", self, "state", False]
        self.properties["pneumatic"] = ["list", self.format['pneumatics'], None]

sequence_types =   ["Path",       "Motor",       "Flag",       "TurnFor",       "DriveFor",       "WaitFor",        "SetPneumatic"]
sequence_classes = [SequencePath, SequenceMotor, SequenceFlag, SequenceTurnFor, SequenceDriveFor, SequenceSleepFor, SequenceSetPneumatic]
