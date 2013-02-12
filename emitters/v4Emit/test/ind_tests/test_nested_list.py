#!/usr/bin/env python

import os
import sys

sys.path.append(
    os.path.join('../../lib/'))

import wVariables
import commitManager
import invalidationListener

'''
Puts lists inside of lists.  Want to ensure that if we write to list
elements, which are themselves lists, that if we modify one of the
elements separately, we'll:
  a) see that change reflected in the original list
  b) we won't get read/write collisions between element lists and
     master lists
  c) we can still perform operations in parallel between the master
     list and element lists so long as those do not affect each other.
     
'''

class BasicTestInvalidationListener(invalidationListener._InvalidationListener):
    def notify_invalidated(self,wld_obj):
        pass
    

def create_two_events(commit_manager):
    evt1 = BasicTestInvalidationListener(commit_manager)
    evt2 = BasicTestInvalidationListener(commit_manager)
    return evt1,evt2

def create_list(commit_manager,to_populate_with):
    '''
    @param {list} to_populate_with --- Each element gets appended to
    the list that we return.  This can be a list of value types, or a
    list of Waldo's internal lists.
    '''
    new_list = wVariables.WaldoListVariable()
    evt1,evt2 = create_two_events(commit_manager)
    for element in to_populate_with:
        new_list.get_val(evt1).append_val(evt1,element)

    evt1.hold_can_commit()
    evt1.complete_commit()

    return new_list
        
    

def run_test():
    commit_manager = commitManager._CommitManager()

    el1_list = create_list(commit_manager,[0,1,2])
    el2_list = create_list(commit_manager,[3,4,5])
    el3_list = create_list(commit_manager,[6,7,8])

    master_list = create_list(
        commit_manager,[el1_list,el2_list,el3_list])


    # first: test that if we delete the last element of el3_list (via
    # el3_list) and delete the first element of el1_list (via master
    # list), both can commit.  then, check that both changes were
    # visible to the other.
    evt1,evt2 = create_two_events(commit_manager)
    el3_list.get_val(evt1).del_key_called(evt1,2)
    master_list.get_val(evt2).get_val_on_key(evt2,0).get_val(evt2).del_key_called(evt2,0)

    if not evt1.hold_can_commit():
        print '\nErr: should be able to hold commit 1\n'
        return False
    if not evt2.hold_can_commit():
        print '\nErr: should be able to hold commit 2\n'
        return False
    
    evt1.complete_commit()
    evt2.complete_commit()

    # now check that the changes were actually applied 
    evt1,evt2 = create_two_events(commit_manager)
    if master_list.get_val(evt1).get_val_on_key(evt1,2).get_val(evt1).contains_key_called(evt1,2):
        err_msg = '\nCould not see change made to last element of '
        err_msg += 'array made from master.\n'
        print err_msg
        return False

    if el1_list.get_val(evt2).get_len(evt2) != 2:
        err_msg = '\nCould not see change made to first element of '
        err_msg += 'array made from el1 list.\n'
        print err_msg
        return False
        
    if not evt1.hold_can_commit():
        print '\nerr: should be able to commit\n'
        return False
    evt1.complete_commit()
    
    if not evt2.hold_can_commit():
        print '\nerr: should be able to commit 2 reads\n'
        return False
    evt2.complete_commit()
        

    # try to perform an append operation on one list while performing
    # a len on it.  Should only be able to commit one.
    evt1,evt2 = create_two_events(commit_manager)
    master_list.get_val(evt1).get_val_on_key(evt1,0).get_val(evt1).append_val(evt1,55)
    el1_list.get_val(evt2).get_len(evt2)

    if not evt1.hold_can_commit():
        err_msg = '\nerr: should be able to commit master list change\n'
        print err_msg
        return False
    evt1.complete_commit()
    
    if evt2.hold_can_commit():
        err_msg = '\nerr: should not be able to commit because of dual change\n'
        print err_msg
        return False
    evt2.backout_commit(True)    


    return True
    
        
if __name__ == '__main__':
    run_test()


