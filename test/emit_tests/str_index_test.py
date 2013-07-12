#!/usr/bin/env python
from str_index_test_v4 import StrTester
import sys,os
base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..')
sys.path.append(base_dir)
from waldo.lib import Waldo


def run_test():
    str_tester = Waldo.no_partner_create(StrTester)
    if str_tester.return_str() != 'h':
        return False
    return True


if __name__ == '__main__':
    if run_test():
        print '\nSucceeded\n'
    else:
        print '\nFailed\n'
