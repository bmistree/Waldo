import sys
import os
sys.path.append(os.path.join("../../waldo/lib"))
sys.path.append(os.path.join("../../"))
from waldo.lib import Waldo
from wVariables import WaldoListVariable
from Waldo import _host_uuid
from internal_list import IList



class GUI_Draw(WaldoListVariable):

    def __init__(self, draw):
        WaldoListVariable.__init__(self, "", _host_uuid)
        self.val = IList(draw)


    def complete_commit(self, invalid_listener):
        super(GUI_Draw, self).complete_commit(invalid_listener)
