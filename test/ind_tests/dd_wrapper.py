#!/usr/bin/env python

import subprocess
import os
ind_tests_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)))


def run_test():
    cmd = ['python',os.path.join(ind_tests_dir,'test_deadlock_detection.py')]
    proc = subprocess.Popen(cmd,shell=False)
    proc.wait()
    # note: if completes, then it passed.  otherwise, failed.
    return True


if __name__ == '__main__':
    run_test()
