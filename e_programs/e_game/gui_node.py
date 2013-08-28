import sys
import os
sys.path.append(os.path.join("../../waldo/lib"))
sys.path.append(os.path.join("../../"))
from waldo.lib import Waldo
from wVariables import WaldoUserStructVariable
from Waldo import _host_uuid




class GUI_Node(WaldoUserStructVariable):

    def __init__(self, draw):
        self.draw_circle = draw
        WaldoUserStructVariable.__init__(self, "", _host_uuid, False, {})

    def complete_commit(self, invalid_listener):
        dirty_map_elem = self._dirty_map[invalid_listener.uuid]
        node_val = dirty_map_elem.val.de_waldoify(invalid_listener)
        print 'node_val'
        print node_val
        if len(node_val) > 0:
            OGLInitialize() 
            self.draw_circle(node_val)
        super(GUI_Node, self).complete_commit(invalid_listener)
