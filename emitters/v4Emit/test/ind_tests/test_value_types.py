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
    
    def notify_invalidated(self,wld_obj):
        notify_msg = '\nWarning: ' + str(self.uuid)
        notify_msg += ' got an invalidation for object '
        notify_msg += str(wld_obj.uuid) + '.\n'
        print notify_msg
        
        

def setup():
    commit_manager = commitManager._CommitManager()
    evt1 = PrintTestInvalidationListener(commit_manager)
    evt2 = PrintTestInvalidationListener(commit_manager)
    number = wVariables.WaldoNumVariable(31)
    text = wVariables.WaldoTextVariable('ab')
    tf = wVariables.WaldoTrueFalseVariable(True)

    return evt1,evt2,number,text,tf
    
def run():
    evt1,evt2,number,text,tf = setup()

    print '\n\n'
    print (number.get_val(evt1))
    print '\n\n'
    number.write_val(evt1,2)
    text.write_val(evt1,'hi')
    tf.write_val(evt1, False)
    print (number.get_val(evt1))
    print '\n\n'
    print (number.get_val(evt2))
    print (text.get_val(evt2))
    print (tf.get_val(evt2))    
    print '\n\n'    

    if not evt1.hold_can_commit():
        print '\nError: should be able to commit a single committer.\n'
    else:
        evt1.complete_commit()

    time.sleep(2)

    print (number.get_val(evt1))

    
    if evt2.hold_can_commit():
        print '\nError: should have been unable to commit second event.\n'
    else:
        evt2.backout_commit(True)


    print '\n\n'
        

if __name__ == '__main__':
    run()


