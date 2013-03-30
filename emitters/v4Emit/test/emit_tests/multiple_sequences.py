#!/usr/bin/env python


from multiple_sequences_v4 import SideA, SideB
import os,sys
lib_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..',
    '..','lib')
sys.path.append(lib_dir)
import Waldo


# really just used for debugging the test case
def print_debug(endpoint,to_print):
    print to_print

def run_test():
    sideA, sideB = (
        Waldo.same_host_create(
            SideA,print_debug).same_host_create(SideB,print_debug))

    texta, textb = ('a','b')
    received_texta, received_textb = sideA.test_two_sequences(texta,textb)
    if (received_texta != texta) or (received_textb != textb):
        err_msg = '\nError: did not get correct values back when '
        err_msg += 'initiating a 2-sequence test'
        print err_msg
        return False
    
    return True


if __name__ == '__main__':
    run_test()
