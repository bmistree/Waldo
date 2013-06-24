#!/usr/bin/env python

from single_thread_references_v4 import SingleSide

import sys,os
base_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..','..')
sys.path.append(base_dir)
from waldo.lib import Waldo


def run_test():
    single_side = Waldo.no_partner_create(SingleSide)

    single_side.populate_lists()
    single_side.change_one()
    len_a, len_b1, len_b2 = single_side.get_len_lists()

    if (len_a != 3) or (len_b1 != 3) or (len_b2 != 3):
        return False

    return True


if __name__ == '__main__':
    run_test()
