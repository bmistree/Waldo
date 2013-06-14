#!/usr/bin/env python

import os, sys,test_util
base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..',)
sys.path.append(base_dir)
from waldo.lib import wVariables, util

'''
Tests a basic value map to ensure that can and cannot perform certain
operations concurrently and that operations are committed.
'''

host_uuid = util.generate_uuid()


def create_two_events(dummy_endpoint):
    evt1 = dummy_endpoint._act_event_map.create_root_event()
    evt2 = dummy_endpoint._act_event_map.create_root_event()
    return evt1,evt2
        
def run_test():
    # initialize and populate list to be [1,2,3]
    dummy_endpoint = test_util.DummyEndpoint(
        test_util.SingleEndpointConnectionObj(),host_uuid)
    wlist = wVariables.WaldoListVariable('some list',host_uuid)
    evt1,evt2 = create_two_events(dummy_endpoint)
    wlist.get_val(evt1).append_val(evt1,1)
    wlist.get_val(evt1).append_val(evt1,2)
    wlist.get_val(evt1).append_val(evt1,3)    
    evt1.hold_can_commit()
    evt1.complete_commit()
    
    
    evt1,evt2 = create_two_events(dummy_endpoint)
    # wlist.get_val(evt1)._print_values()
    
    # testing to ensure that can perform reads simultaneously
    if wlist.get_val(evt1).get_val_on_key(evt1,0) != 1:
        print ('\nerr: expected 1\n')
        print (wlist.get_val(evt1).get_val_on_key(evt1,0))
        print (wlist.get_val(evt1))
        print ('\n\n')
        return False

    if wlist.get_val(evt2).get_val_on_key(evt2,0) != 1:
        print ('\nerr: expected 3\n')
        return False

    if not evt1.hold_can_commit():
        print ('\nerr: should be able to commit\n')
        return False
    evt1.complete_commit()
    
    if not evt2.hold_can_commit():
        print ('\nerr: should be able to commit 2 reads\n')
        return False
    evt2.complete_commit()

    # testing to ensure that cannot simultaneously commit a read to a
    # data cell after have writtent to it.
    evt1,evt2 = create_two_events(dummy_endpoint)

    # start read on index.  
    if wlist.get_val(evt1).get_val_on_key(evt1,1) != 2:
        print ('\nerr: expected 2\n')
        return False

    # before committing read, perform write on same index
    wlist.get_val(evt2).write_val_on_key(evt2,1,5)
    if not evt2.hold_can_commit():
        print ('\nerr: should be able commit write of 5\n')
        return False
    evt2.complete_commit()

    if evt1.hold_can_commit():
        err_msg = '\nerr: should not be able to finish read commit '
        err_msg += 'with intefering write\n'
        print (err_msg)
        return False
    evt1.backout_commit()

    # testing to ensure can write to one element and write to another
    # element
    evt1,evt2 = create_two_events(dummy_endpoint)
    wlist.get_val(evt1).write_val_on_key(evt1,1,3)
    wlist.get_val(evt2).write_val_on_key(evt2,2,4)
    
    if not evt1.hold_can_commit():
        print ('\nerr: should have been able to commit the write 3\n')
        return False
    evt1.complete_commit()
    if not evt2.hold_can_commit():
        print ('\nerr: should have been able to commit the write 4\n')
        return False
    evt2.complete_commit()

    # check to ensure that the correct values were written in above
    # steps + check to ensure that deletion of an element prevents
    # committing to it.
    evt1,evt2 = create_two_events(dummy_endpoint)
    if wlist.get_val(evt2).get_val_on_key(evt2,1) != 3:
        print ('\nshould have gotten 3 from prev commit\n')
        return False
    if wlist.get_val(evt2).get_val_on_key(evt2,2) != 4:
        print ('\nshould have gotten 4 from prev commit\n')
        return False

    wlist.get_val(evt1).del_key_called(evt1,1)
    if not evt1.hold_can_commit():
        print ('\nerr: should have been able to commit del')
        return False
    evt1.complete_commit()

    if evt2.hold_can_commit():
        print ('\nerr: should not have been able to hold print commit ')
        return False
    evt2.backout_commit()

    # check to ensure last delete was correct and that we cannot call
    # keys and append simultaneoulsy.
    evt1,evt2 = create_two_events(dummy_endpoint)
    length = wlist.get_val(evt1).get_len(evt1)
    if length != 2:
        print ('\nerr: expecting length of 2 after delete\n')
        return False

    # before commit len, append and commit append....should not be
    # able to commit len after that.
    wlist.get_val(evt2).append_val(evt2,5)
    if not evt2.hold_can_commit():
        print ('\nerr: should be able to commit append\n')
        return False
    evt2.complete_commit()
    
    if evt1.hold_can_commit():
        print ('\nerr: cannot commit len if appended in meantime.\n')
        return False
    evt1.backout_commit()

    return True
    
        
if __name__ == '__main__':
    run_test()


