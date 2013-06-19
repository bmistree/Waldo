#!/usr/bin/env python
import os,sys
base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..')
sys.path.append(base_dir)
from waldo.lib import Waldo

from single_side_stop_v4 import SingleSide


def run_test():
    single_side = Waldo.no_partner_create(SingleSide)
    single_side.do_nothing()
    single_side.stop()
    try:
        single_side.do_nothing()
    except Waldo.StoppedException as inst:
        return True

    return False

if __name__ == '__main__':
    run_test()
