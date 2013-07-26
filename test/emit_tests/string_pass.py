#!/usr/bin/env python

from string_pass_v4 import one_side,other_side

import sys,os,time
base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..')
sys.path.append(base_dir)
from waldo.lib import Waldo


def run_test():
    single_side, ow = Waldo.same_host_create(one_side).same_host_create(other_side)
    single_side.single_string()
    single_side.do_it(ow);
    time.sleep(5)
    return True


if __name__ == '__main__':

    if run_test():
        print '\nSucceeded\n'
    else:
        print '\nFailed\n'
