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
    dummy_endpoint = test_util.DummyEndpoint(
        test_util.SingleEndpointConnectionObj(),host_uuid)
    
    wmap = wVariables.WaldoMapVariable('some map',host_uuid)

    evt1,evt2 = create_two_events(dummy_endpoint)
    wmap.get_val(evt1).add_key(evt1,'a',1)
    wmap.get_val(evt1).add_key(evt1,'b',2)
    evt1.hold_can_commit()
    evt1.complete_commit()
    
    evt1,evt2 = create_two_events(dummy_endpoint)

    # # testing to ensure that can perform reads simultaneously
    if wmap.get_val(evt1).get_val_on_key(evt1,'a') != 1:
        print '\nerr: expected 1\n'
        return False

    if wmap.get_val(evt2).get_val_on_key(evt2,'a') != 1:
        print '\nerr: expected 1\n'
        return False

    if not evt1.hold_can_commit():
        print '\nerr: should be able to commit\n'
        return False
    evt1.complete_commit()
    
    if not evt2.hold_can_commit():
        print '\nerr: should be able to commit 2 reads\n'
        return False
    else:
        evt2.backout_commit()


    # testing to ensure that cannot simultaneously commit a read to a
    # data cell after have writtent to it.        
    evt1,evt2 = create_two_events(dummy_endpoint)
    
    # start read on index
    if wmap.get_val(evt1).get_val_on_key(evt1,'b') != 2:
        print '\nerr: expected 2\n'
        return False

    # before committing read, perform write on same index and commit
    # the write.
    wmap.get_val(evt2).write_val_on_key(evt2,'b',5)
    if not evt2.hold_can_commit():
        print '\nerr: should be able to commit after having written 5\n'
        return False
    evt2.complete_commit()

    
    if evt1.hold_can_commit():
        err_msg = '\nerr: should be not able to commit read element '
        err_msg += 'after write has committed to it'
        print err_msg
        return False
    evt1.backout_commit()

    
    # testing to ensure can write to one element and write to another
    # element
    evt1,evt2 = create_two_events(dummy_endpoint)
    wmap.get_val(evt1).write_val_on_key(evt1,'a',3)
    wmap.get_val(evt2).write_val_on_key(evt2,'b',1)
    
    if not evt1.hold_can_commit():
        print '\nerr: should have been able to commit the write 3\n'
        return False
    evt1.complete_commit()
    if not evt2.hold_can_commit():
        print '\nerr: should have been able to commit the write 1\n'
        return False
    evt2.complete_commit()

    # check to ensure that the correct values were written in above
    # steps + check to ensure that deletion of an element prevents
    # committing to it.
    evt1,evt2 = create_two_events(dummy_endpoint)
    if wmap.get_val(evt2).get_val_on_key(evt2,'a') != 3:
        print '\nshould have gotten 3 from prev commit\n'
        return False
    if wmap.get_val(evt2).get_val_on_key(evt2,'b') != 1:
        print '\nshould have gotten 1 from prev commit\n'
        return False

    wmap.get_val(evt1).del_key_called(evt1,'b')
    if not evt1.hold_can_commit():
        print '\nerr: should have been able to commit del'
        return False
    evt1.complete_commit()

    if evt2.hold_can_commit():
        print '\nerr: should not have been able to hold print commit '
        return False
    evt2.backout_commit()

    # check to ensure last delete was correct and that we cannot call
    # keys and add_key simultaneoulsy.
    evt1,evt2 = create_two_events(dummy_endpoint)
    keys = list(wmap.get_val(evt1).get_keys(evt1))
    if 'a' not in keys:
        print '\nerr: expecting key a\n'
        return False
    if 'b' in keys:
        print '\nerr: not expecting key b\n'
        return False

    # before can commit keys call, add a key and commit that action,
    # should force backout of keys
    wmap.get_val(evt2).add_key(evt2,'m',3)
    if not evt2.hold_can_commit():
        print '\nerr: should have been able to commit add key\n'
        return False
    evt2.complete_commit()
    
    if evt1.hold_can_commit():
        print '\nerr: should not have been able to commit keys after add_key\n'
        return False
    evt1.backout_commit()


    return True
        

if __name__ == '__main__':
    run_test()


