#!/usr/bin/env python

import os
import sys

sys.path.append(
    os.path.join('..','lib'))



import ind_tests.test_nested_list
import ind_tests.test_num
import ind_tests.test_value_list
import ind_tests.test_value_map



TO_RUN = [
    ('Nested list', ind_tests.test_nested_list.run_test),
    ('Basic num test', ind_tests.test_num.run_test),
    ('List of values', ind_tests.test_value_list.run_test),
    ('Map of values', ind_tests.test_value_map.run_test),
    ]

def run_all():

    for to_run_tuple in TO_RUN:
        test_name = to_run_tuple[0]
        test_method = to_run_tuple[1]

        print '\nRunning test ' + test_name + '\n'
        succeeded = test_method()
        print '\n........',
        if succeeded:
            print 'SUCCESS'
        else:
            print 'FAILURE'
        print '\n\n'


if __name__ == '__main__':
    run_all()
