#!/usr/bin/env python

import os
import sys

sys.path.append(
    os.path.join('../lib/'))

import wObjects
import commitManager
import invalidationListener

'''
Tests a basic value map to ensure that can and cannot perform certain
operations concurrently and that operations are committed.
'''


class BasicTestInvalidationListener(invalidationListener._InvalidationListener):
    def notify_invalidated(self,wld_obj):
        pass
    

def create_two_events(commit_manager):
    evt1 = BasicTestInvalidationListener(commit_manager)
    evt2 = BasicTestInvalidationListener(commit_manager)
    return evt1,evt2
        
def run_test():
    wObjects.initialize()
    commit_manager = commitManager._CommitManager()
    wmap = wObjects.WaldoMap()

    evt1,evt2 = create_two_events(commit_manager)
    wmap.get_val(evt1).add_key(evt1,'a',1)
    wmap.get_val(evt1).add_key(evt1,'b',2)
    evt1.hold_can_commit()
    evt1.complete_commit()
    
    evt1,evt2 = create_two_events(commit_manager)

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
        evt2.backout_commit(True)

    # testing to ensure that cannot simultaneously commit a read and a
    # write to the same cell.
    evt1,evt2 = create_two_events(commit_manager)
    if wmap.get_val(evt1).get_val_on_key(evt1,'b') != 2:
        print '\nerr: expected 2\n'
        return False
    wmap.get_val(evt2).write_val_on_key(evt2,'b',5)
    if not evt1.hold_can_commit():
        print '\nerr: should be able to commit 5\n'
        return False
    evt1.complete_commit()

    if evt2.hold_can_commit():
        print '\nerr: should not be able to read after having written 5\n'
        return False
    evt2.backout_commit(True)

    # testing to ensure can write to one element and write to another
    # element
    evt1,evt2 = create_two_events(commit_manager)
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
    evt1,evt2 = create_two_events(commit_manager)
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
    evt2.backout_commit(True)

    # check to ensure last delete was correct and that we cannot call
    # keys and append simultaneoulsy.
    evt1,evt2 = create_two_events(commit_manager)
    keys = list(wmap.get_val(evt1).get_keys(evt1))
    if 'a' not in keys:
        print '\nerr: expecting key a\n'
        return False
    if 'b' in keys:
        print '\nerr: not expecting key b\n'
        return False

    wmap.get_val(evt2).add_key(evt2,'m',3)
    if not evt1.hold_can_commit():
        print '\nerr: should have been able to commit keys\n'
        return False
    evt1.complete_commit()

    if evt2.hold_can_commit():
        print '\nerr: should not have been able to commit append\n'
        return False
    evt2.backout_commit(True)

        

if __name__ == '__main__':
    run_test()


