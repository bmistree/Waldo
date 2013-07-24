import os
import sys

sys.path.append(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        '..','..'))

from waldo.lib.waldoLockedActiveEvent import RootEventParent,LockedActiveEvent
from waldo.lib.util import generate_uuid

class _DummyActiveEventMap(object):
    def __init__(self):
        self.map = {}
    def add_event(self,evt):
        self.map[evt.uuid] = evt
    def remove_event(self,evt_uuid):
        del self.map[evt_uuid]
        

class DummyEndpoint(object):
    def __init__(self):
        self.evt_map = _DummyActiveEventMap()

    def create_root_event(self):
        rep = RootEventParent(generate_uuid())
        return LockedActiveEvent(rep,self.evt_map)


