import sys
import os
sys.path.append(os.path.join("../../waldo/lib"))
sys.path.append(os.path.join("../../"))
from waldo.lib import Waldo
from wVariables import WaldoExtListVariable, WaldoListVariable
from Waldo import _host_uuid




class GUI_Arc(WaldoListVariable):

    def __init__(self, draw):
        self.draw_arc = draw
        WaldoListVariable.__init__(self, "", _host_uuid, False, {})

    def complete_commit(self, invalid_listener):
        dirty_map_elem = self._dirty_map[invalid_listener.uuid]
        arc_val = dirty_map_elem.val
        self.draw_arc(arc_val[0], arc_val[1], arc_val[2], arc_val[3])
        super(GUI_Arc, self).complete_commit(invalid_listener)

class GUI_Arc_Ext(WaldoExtListVariable):

    def __init__(self, draw_funct):
        gui_arc = GUI_Arc(draw_funct)
        WaldoExtListVariable.__init__(self, "", _host_uuid, False, gui_arc)
