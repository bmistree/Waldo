import sys
import os
sys.path.append(os.path.join("../../waldo/lib"))
sys.path.append(os.path.join("../../"))
from waldo.lib import Waldo
from wVariables import WaldoListVariable
from Waldo import _host_uuid




class GUI_Arc(WaldoListVariable):

    def __init__(self, draw):
        self.draw_arc = draw
        WaldoListVariable.__init__(self, "", _host_uuid)

    def complete_commit(self, invalid_listener):
        dirty_map_elem = self._dirty_map[invalid_listener.uuid]
        arc_val = dirty_map_elem.val.de_waldoify(invalid_listener)
        print 'arc_val'
        print arc_val
        if len(arc_val) > 0:
            OGLInitialize() 
            self.draw_arc(arc_val)
        super(GUI_Arc, self).complete_commit(invalid_listener)
