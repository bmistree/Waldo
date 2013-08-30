import sys
import os
sys.path.append(os.path.join("../../waldo/lib"))
sys.path.append(os.path.join("../../"))
from waldo.lib import Waldo
from wVariables import WaldoExtTextVariable, WaldoTextVariable
from Waldo import _host_uuid




class GUI_Score(WaldoTextVariable):

    def __init__(self, gui_score):
        self.score_label = gui_score
        WaldoTextVariable.__init__(self, "", _host_uuid, False, "")

    def complete_commit(self, invalid_listener):
        dirty_map_elem = self._dirty_map[invalid_listener.uuid]
        score = dirty_map_elem.val
        self.score_label.SetLabel(score.replace(".0", ""))
        super(GUI_Score, self).complete_commit(invalid_listener)

class GUI_Score_Ext(WaldoExtTextVariable):

    def __init__(self, gui_obj):
        gui_num = GUI_Score(gui_obj)
        WaldoExtTextVariable.__init__(self, "", _host_uuid, False, gui_num)
