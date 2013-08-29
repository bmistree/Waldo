import sys
import os
sys.path.append(os.path.join("../../waldo/lib"))
sys.path.append(os.path.join("../../"))
sys.path.append(os.path.join("../../waldo"))
from waldoInternalMap import InternalMap
from waldo.lib import Waldo
from Waldo import _host_uuid
from wx.lib.ogl import *



class IMap(InternalMap):

    def __init__(self, draw):
        self.draw_circle = draw
        InternalMap.__init__(self, _host_uuid, False, {})

    def complete_commit(self, invalid_listener):
        dirty_map_elem = self._dirty_map[invalid_listener.uuid]
        print dirty_map_elem
        node_vals = dirty_map_elem.val
        print node_vals
        self.draw_circle(node_vals)
        super(IMap, self).complete_commit(invalid_listener)

