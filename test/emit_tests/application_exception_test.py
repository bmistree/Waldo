#!/usr/bin/env python

import sys,os
base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..')
sys.path.append(base_dir)

from waldo.lib import Waldo
from application_exception_test_v4 import SingleSide

def run_test():
   testEndpoint = Waldo.no_partner_create(SingleSide) 
   return testEndpoint.testApplicationException()

if __name__ == "__main__":
    run_test()
