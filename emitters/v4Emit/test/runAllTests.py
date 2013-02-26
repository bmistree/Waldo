#!/usr/bin/env python

import os
import sys

sys.path.append(
    os.path.join('..','lib'))



import ind_tests.test_nested_list
import ind_tests.test_num
import ind_tests.test_value_list
import ind_tests.test_value_map
import ind_tests.test_peered_nested_map_list
import ind_tests.test_serialized_deserialized_num
import ind_tests.test_serialized_deserialized_nested_map
import ind_tests.test_single_request_block_between_endpoints_sequence_local_data
import ind_tests.test_single_request_block_between_endpoints_peered_data
import ind_tests.test_reschedule_on_conflict

TO_RUN = [
    ('Nested list', ind_tests.test_nested_list.run_test),
    ('Basic num test', ind_tests.test_num.run_test),
    ('List of values', ind_tests.test_value_list.run_test),
    ('Map of values', ind_tests.test_value_map.run_test),
    ('Map of values', ind_tests.test_value_map.run_test),
    ('Nested peered list', ind_tests.test_peered_nested_map_list.run_test),
    
    ('Serialization of single number',
     ind_tests.test_serialized_deserialized_num.run_test),

    ('Serialization of a nested map',
     ind_tests.test_serialized_deserialized_nested_map.run_test),

    ('Test update of sequence local data no commit',
     ind_tests.test_single_request_block_between_endpoints_sequence_local_data.run_test),
    
    ('Test update of peered data + commit',
     ind_tests.test_single_request_block_between_endpoints_peered_data.run_test),

    ('Test reschedule root on conflict',
     ind_tests.test_reschedule_on_conflict.run_test),
    ]

def run_all():

    for to_run_tuple in TO_RUN:
        test_name = to_run_tuple[0]
        test_method = to_run_tuple[1]

        print '\nRunning test ' + test_name 
        succeeded = test_method()
        print '........',
        if succeeded:
            print 'SUCCESS'
        else:
            print 'FAILURE'
        print '\n\n'


if __name__ == '__main__':
    run_all()
