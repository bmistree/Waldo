#!/usr/bin/env python

import os
import sys
import subprocess
sys.path.append(
    os.path.join('..','waldo','lib'))


import locked_tests.chained_endpoint_call_no_conflict_test
import locked_tests.endpoint_call_no_conflict_test
import locked_tests.no_conflict_test
import locked_tests.preempted_chained_endpoint_call
import locked_tests.preemption_test
import locked_tests.read_read_test
import locked_tests.partner_no_conflict_test
import locked_tests.list_map_write_no_conflict
import locked_tests.list_map_write_conflict
import locked_tests.concurrent_map
import locked_tests.partner_seq_local_test

def run_lib_tests():
    to_run = [
        ('Chained endpoint call with no conflict', locked_tests.chained_endpoint_call_no_conflict_test.run_test),
        ('Single endpoint call with no conflict', locked_tests.endpoint_call_no_conflict_test.run_test),
        ('Single event, no conflict', locked_tests.no_conflict_test.run_test),
        ('Preempted, chained endpoint call', locked_tests.preempted_chained_endpoint_call.run_test),
        ('Preempted single endpoint', locked_tests.preemption_test.run_test),
        ('Concurrent reads', locked_tests.read_read_test.run_test),
        ('Partner writes', locked_tests.partner_no_conflict_test.run_test),
        ('Non-conflicting writes to list and map', locked_tests.list_map_write_no_conflict.run_test),
        ('Conflicting writes to list and map', locked_tests.list_map_write_conflict.run_test),
        ('Concurrent writes on different map elements',locked_tests.concurrent_map.run_test),
        ('Sequence local data',locked_tests.partner_seq_local_test.run_test),
        ]
    run_tests(to_run)

def run_tests(to_run):
    print ('\n\n')
    for to_run_tuple in to_run:
        test_name = to_run_tuple[0]
        test_method = to_run_tuple[1]

        print ('\nRunning test ' + test_name )
        succeeded = test_method()
        success_failure_msg = '.......'
        if succeeded:
            success_failure_msg += 'SUCCESS'
        else:
            success_failure_msg += 'FAILURE'

        print (success_failure_msg)
    print( '\n\n')

    

def run_all():
    run_lib_tests()


if __name__ == '__main__':
    run_all()
