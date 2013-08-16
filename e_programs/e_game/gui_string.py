import sys
import os
sys.path.append(os.path.join("../../waldo/lib"))
from wVariables import WaldoExtTextVariable, WaldoTextVariable
from Waldo import _host_uuid




class GUI_String(WaldoTextVariable):

    def __init__(self, gui_window):
        self.txt_window = gui_window
        WaldoTextVariable.__init__(self, "", _host_uuid, False, "")

    def complete_commit(self, invalid_listener):
        dirty_map_elem = self._dirty_map[invalid_listener.uuid]
        txt_val = dirty_map_elem.val
        self.txt_window.AppendText(txt_val)
        super(GUI_String, self).complete_commit(invalid_listener)

class GUI_String_Ext(WaldoExtTextVariable):

    def __init__(self, gui_obj):
        gui_str = GUI_String(gui_obj)
        WaldoExtTextVariable.__init__(self, "", _host_uuid, False, gui_str)
