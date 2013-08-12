#!/usr/bin/env python
import os
import sys

base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..')
sys.path.append(base_dir)
from waldo.lib import Waldo
from application_exception_endpoint_call_test_v4 import SingleSide
from multiprocessing import Process

def run_test():
    thrower = Waldo.no_partner_create(SingleSide, None)
    catcher = Waldo.no_partner_create(SingleSide, thrower)
    return catcher.test_catch()

if __name__ == "__main__":
    print run_test()
