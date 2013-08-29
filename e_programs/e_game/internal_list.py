import sys
import os
sys.path.append(os.path.join("../../waldo/lib"))
sys.path.append(os.path.join("../../"))
sys.path.append(os.path.join("../../waldo"))
from waldoInternalList import InternalList
from waldo.lib import Waldo
from Waldo import _host_uuid
from wx.lib.ogl import *



class Test(InternalList):

    def __init__(self, draw):
        self.draw_arc = draw
        InternalList.__init__(self, _host_uuid, False, [])

    def complete_commit(self, invalid_listener):
        dirty_map_elem = self._dirty_map[invalid_listener.uuid]
        print dirty_map_elem
        arc_vals = dirty_map_elem.val
        self.draw_arc(arc_vals)
        print "Test complete commit executed"
        super(Test, self).complete_commit(invalid_listener)

