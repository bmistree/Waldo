import sys
import os
sys.path.append(os.path.join("../../waldo/lib"))
sys.path.append(os.path.join("../../"))
from waldo.lib import Waldo
from wVariables import WaldoUserStructVariable
from Waldo import _host_uuid
from internal_map import IMap



class GUI_Node(WaldoUserStructVariable):

    def __init__(self, draw):
        WaldoUserStructVariable.__init__(self, "", _host_uuid, False, {})
        self.val = IMap(draw)

    def complete_commit(self, invalid_listener):
        super(GUI_Node, self).complete_commit(invalid_listener)
