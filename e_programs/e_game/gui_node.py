import sys
import os
sys.path.append(os.path.join("../../waldo/lib"))
sys.path.append(os.path.join("../../"))
from waldo.lib import Waldo
from wVariables import WaldoExtUserStructVariable, WaldoUserStructVariable
from Waldo import _host_uuid




class GUI_Node(WaldoUserStructVariable):

    def __init__(self, draw):
        self.draw_circle = draw
        WaldoUserStructVariable.__init__(self, "", _host_uuid, False, {})

    def complete_commit(self, invalid_listener):
        dirty_map_elem = self._dirty_map[invalid_listener.uuid]
        node_val = dirty_map_elem.val
        self.draw_circle(node_val['x'], node_val['y'], node_val['found'], node_val['node_num'], node_val['answer'])
        super(GUI_Node, self).complete_commit(invalid_listener)

class GUI_Node_Ext(WaldoExtUserStructVariable):

    def __init__(self, draw_funct):
        gui_node = GUI_Node(draw_funct)
        WaldoExtUserStructVariable.__init__(self, "", _host_uuid, False, gui_node)
