#!/usr/bin/env python

import os
import sys

sys.path.append(
    os.path.join('../../lib/'))

import wVariables
import commitManager
import invalidationListener
import time
import waldoNetworkSerializer


class BasicInvalidationListener(invalidationListener._InvalidationListener):
    def __init__(self,*args):
        invalidationListener._InvalidationListener.__init__(self,*args)
        self.notified_invalidated = False
    def notify_invalidated(self,wld_obj):
        self.notified_invalidated = True
        
        

class SingleSide(object):
    def __init__(self):
        # both sides start at 1
        self.number = wVariables.WaldoNumVariable('some num',True,1)
        self.commit_manager = commitManager._CommitManager()
    def new_event(self):
        return BasicInvalidationListener(self.commit_manager)
    

def run_test():
    lhs = SingleSide()
    rhs = SingleSide()

    lhs_event = lhs.new_event()
    rhs_event = rhs.new_event()


    # make a change to lhs' number and try to update rhs' number.
    # ensure they can both commit the change.
    lhs.number.write_val(lhs_event,2)
    serializabled = lhs.number.serializable_var_tuple_for_network(
        'some_name',lhs_event)

    waldoNetworkSerializer.deserialize_peered_object_into_variable(
        serializabled,rhs_event,rhs.number)

    if not lhs_event.hold_can_commit():
        print '\nError: should be able to commit lhs.\n'
        return False
    lhs_event.complete_commit()


    if not rhs_event.hold_can_commit():
        print '\nError: should be able to commit rhs.\n'
        return False
    rhs_event.complete_commit()


    # check that both sides have the new number
    lhs_event = lhs.new_event()
    rhs_event = rhs.new_event()
    
    if lhs.number.get_val(lhs_event) != 2:
        print '\nErr: for some reason, did not commit on lhs.\n'
        return False

    if rhs.number.get_val(rhs_event) != 2:
        print '\nErr: for some reason, did not commit on rhs.\n'
        return False


    if not lhs_event.hold_can_commit():
        print '\nError: should be able to commit lhs second time.\n'
        return False
    lhs_event.complete_commit()


    if not rhs_event.hold_can_commit():
        print '\nError: should be able to commit rhs second time.\n'
        return False
    rhs_event.complete_commit()

    
    return True
    
    

        

if __name__ == '__main__':
    run_test()


