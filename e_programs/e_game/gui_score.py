import sys
import os
sys.path.append(os.path.join("../../waldo/lib"))
sys.path.append(os.path.join("../../"))
from waldo.lib import Waldo
from wVariables import WaldoExtNumVariable, WaldoNumVariable
from Waldo import _host_uuid




class GUI_Score(WaldoNumVariable):

    def __init__(self, gui_score):
        self.score_label = gui_score
        WaldoNumVariable.__init__(self, "", _host_uuid, False, "")

    def complete_commit(self, invalid_listener):
        dirty_map_elem = self._dirty_map[invalid_listener.uuid]
        score = dirty_map_elem.val
        self.score_label.SetLabel(str(score).replace(".0", ""))
        super(GUI_Score, self).complete_commit(invalid_listener)

class GUI_Score_Ext(WaldoExtNumVariable):

    def __init__(self, gui_obj):
        gui_num = GUI_Score(gui_obj)
        WaldoExtNumVariable.__init__(self, "", _host_uuid, False, gui_num)
