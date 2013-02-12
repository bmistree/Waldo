#!/usr/bin/env python

import os
import sys

sys.path.append(
    os.path.join('../../lib/'))

import wVariables
import commitManager
import invalidationListener
import time

class PrintTestInvalidationListener(invalidationListener._InvalidationListener):

    def __init__(self,*args):
        invalidationListener._InvalidationListener.__init__(self,*args)
        self.notified_invalidated = False
    
    def notify_invalidated(self,wld_obj):
        self.notified_invalidated = True
        # notify_msg = '\nWarning: ' + str(self.uuid)
        # notify_msg += ' got an invalidation for object '
        # notify_msg += str(wld_obj.uuid) + '.\n'
        # print notify_msg
        
        
INITIAL_NUMBER = 31
def setup():
    commit_manager = commitManager._CommitManager()
    evt1 = PrintTestInvalidationListener(commit_manager)
    evt2 = PrintTestInvalidationListener(commit_manager)
    number = wVariables.WaldoNumVariable(INITIAL_NUMBER)
    evt3 = PrintTestInvalidationListener(commit_manager)
    
    return evt1,evt2,evt3,number
    
def run():
    evt1,evt2,evt3,number = setup()

    if number.get_val(evt1) != INITIAL_NUMBER:
        err_msg = '\nerror on basic get: expected '
        err_msg += str(INITIAL_NUMBER)
        print err_msg
        return False

    number.write_val(evt1,2)
    if number.get_val(evt1) != 2:
        err_msg = '\nerr on second basic get\n'
        print err_msg
        return False
    

    # evt2 shouldn't know anything about evt1's changes to number.
    if number.get_val(evt2) != INITIAL_NUMBER:
        err_msg = '\nerr basic gets should be isolated\n'
        print err_msg
        return False


    if not evt1.hold_can_commit():
        print '\nError: should be able to commit a single committer.\n'
        return False

    evt1.complete_commit()

    time.sleep(1)

    if not evt2.notified_invalidated:
        err_msg = '\nerr: should have been notified of invalidation'
        print err_msg
        return False

    
    if evt2.hold_can_commit():
        print '\nError: should have been unable to commit second event.\n'
        return False
    evt2.backout_commit(True)

    
    # check that final value is what evt1 committed
    if number.get_val(evt3) != 2:
        print '\nerr: should have seen changes evt1 made.\n'
        return False

    return True


        

if __name__ == '__main__':
    run()


