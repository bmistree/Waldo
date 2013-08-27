#!/usr/bin/env python
import os
import sys

base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..','..','Waldo')
sys.path.append(base_dir)

from waldo.lib import Waldo
from try_finally_test_v4 import Thrower, Catcher

def run_test():
    '''
    Tests the try...finally statement (without the use of catch).

    Returns true if an error may be propagated through a try...finally
    and handled later while having the code in the finally block 
    execute.
    '''
    catcher = Waldo.no_partner_create(Catcher)
    thrower = Waldo.no_partner_create(Thrower)
    catcher.addEndpoint(thrower)
    thrower.addEndpoint(catcher)
    return catcher.testTryFinally()

if __name__ == "__main__":
    print run_test()
