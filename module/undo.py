from module.curves import ComplexCurve, Curve
from sys import getsizeof
from module.sequence import *
from copy import deepcopy

class UndoEvent:
    def __init__(self):
        pass
    def restore(self):
        raise NotImplementedError
    
class UndoManager:
    UNDO_MEM_MAX = 5000
    def __init__(self):
        self.history = []
    
    def add_event(self, event: UndoEvent):
        self.history.append(event)
        if self._size() >= UndoManager.UNDO_MEM_MAX:
            self.history.pop(0)
    
    def _size(self):
        size = 0
        for item in self.history:
            size += getsizeof(item)
        return size

    def undo(self):
        if self.history:
            self.history[-1].restore()
            self.history.pop()

class point:
    class PointMove(UndoEvent):
        def __init__(self, undo_mgr: UndoManager, pos_before, overlap_index: int | None, curve: Curve, index: list[int, int]):
            super().__init__()
            self.pos_before = pos_before
            self.curve = curve
            self.index = index
            self.parent = undo_mgr
            self.overlap_index = overlap_index
        
        def restore(self):
            if self.index[0] == self.index[1]:
                self.curve.move_control(self.index[0], self.pos_before)

                # fix other curve tail
                if self.index[0] == 1:
                    # [1, 1] --> end control point
                    if self.curve.next_curve is not None:
                        # move attached curves start to our end
                        self.curve.next_curve.move_control(0, self.curve.control_points[1][1])
                else:
                    # [0, 0] --> start control point
                    if self.curve.prev_curve is not None:
                        # move attached curves end to our start
                        self.curve.prev_curve.move_control(1, self.curve.control_points[0][0])

                # update overlap point in ComplexCurve to old overlap
                if self.overlap_index is not None:
                    self.curve.parent.overlap_points[self.overlap_index] = self.pos_before

                # recalculate curves
                self.curve.parent.update_all_curves()

            else: # simple weight point movement
                self.curve.control_points[self.index[0]][self.index[1]] = self.pos_before
                self.curve.update_curve()

    class PointDelete(UndoEvent):
        def __init__(self):
            super().__init__()

    class PointAdd(UndoEvent):
        def __init__(self, curve: ComplexCurve):
            super().__init__()
            self.curve = curve
        
        def restore(self):
            self.curve.curves.pop()
            self.curve.overlap_points.pop()

class curve:
    class CurveAdd(UndoEvent):
        def __init__(self, sequence: list, function: SequenceType):
            super().__init__()
            self.sequence = sequence
            self.function = function
        
        def restore(self):
            self.sequence.pop(self.function)

class sequence:
    class SequenceModify(UndoEvent):
        def __init__(self, sequence: list[SequenceType], ui_manager):
            super().__init__()
            """
            Move sequence items back after a change.
            """
            self.sequence = sequence
            self.old_sequence = deepcopy(self.sequence)
            self.ui_manager = ui_manager
        
        def restore(self):
            self.sequence = self.old_sequence
            self.ui_manager.refresh_sequence(self.sequence)
