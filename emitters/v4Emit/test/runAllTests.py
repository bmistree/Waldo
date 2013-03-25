#!/usr/bin/env python

import os
import sys
import subprocess
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
import ind_tests.test_one_side_changes_peered
import ind_tests.test_endpoint_calls
import ind_tests.test_deadlock_detection
import ind_tests.test_de_waldoified

emit_test_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), 'emit_tests')


def run_lib_tests():
    to_run = [
        ('Nested list', ind_tests.test_nested_list.run_test),
        ('Basic num test', ind_tests.test_num.run_test),
        ('List of values', ind_tests.test_value_list.run_test),
        ('Map of values', ind_tests.test_value_map.run_test),
        ('Map of values', ind_tests.test_value_map.run_test),
        ('Nested peered list', ind_tests.test_peered_nested_map_list.run_test),

        ('Test de-waldo-ify', ind_tests.test_de_waldoified.run_test),

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

        ('Test one side changes peered, does other see change?',
         ind_tests.test_one_side_changes_peered.run_test),

        ('Test commit and backout for endpoint calls on external data',
         ind_tests.test_endpoint_calls.run_test),

        ('Test deadlock detection and rollback',
         ind_tests.test_deadlock_detection.run_test),
        
        ]
    run_tests(to_run)

def run_tests(to_run):
    print '\n\n'    
    for to_run_tuple in to_run:
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


def call_make_in_emit_test_folder():
    cwd = os.getcwd()
    os.chdir(emit_test_dir)
    subprocess.call(['make','clean'])
    subprocess.call(['make','v4'])
    os.chdir(cwd)

    
def run_emit_tests():
    '''
    Must be run after 
    '''
    call_make_in_emit_test_folder()

    import emit_tests.set_get_value_test
    import emit_tests.binary_operator_tests
    import emit_tests.tuple_return_tests
    import emit_tests.single_endpoint_initialization_tests
    import emit_tests.two_sided_modify_peer_check_update_test
    import emit_tests.basic_message_sequence_tests
    import emit_tests.conditional_tests
    import emit_tests.pass_references_through_methods
    import emit_tests.sequence_local_data_tests
    import emit_tests.loop_tests
    import emit_tests.misc_tests
    import emit_tests.external_tests
    import emit_tests.sequence_plus_externals_tests
    import emit_tests.basic_endpoint_call_test
    import emit_tests.user_struct_basics
    import emit_tests.oncreate_single_node_test
    import emit_tests.two_sided_oncreate_test
    import emit_tests.network_two_sided_modify_peer_check_update_test
    import emit_tests.self_oncreate_list
    import emit_tests.create_externals_inside_waldo
    import emit_tests.external_reference_tests
    import emit_tests.function_obj_test
    import emit_tests.user_struct_as_library_test
    
    emit_tests_to_run = [
        ('Emit test set endpoint value/get endpoint value',
         emit_tests.set_get_value_test.run_test),

        ('Emit test binary operators',
         emit_tests.binary_operator_tests.run_test),

        ('Emit test tuple returns',
         emit_tests.tuple_return_tests.run_test),

        ('Emit test endpoint and local var initialization',
         emit_tests.single_endpoint_initialization_tests.run_test),

        ('Emit test peered number gets automatically updated when one side writes to it',
         emit_tests.two_sided_modify_peer_check_update_test.run_test),

        ('Emit test update peered data across several sequence blocks',
         emit_tests.basic_message_sequence_tests.run_test),
        
        ('Emit test conditional statements',
         emit_tests.conditional_tests.run_test),

        ('Emit test pass references through methods',
         emit_tests.pass_references_through_methods.run_test),

        ('Emit test sequence local data tests',
         emit_tests.sequence_local_data_tests.run_test),
        
        ('Emit test loops',
         emit_tests.loop_tests.run_test),

        ('Emit test misc',
         emit_tests.misc_tests.run_test),

        ('Emit test externals',
         emit_tests.external_tests.run_test),

        ( ('Emit test coercing externals to value types when' +
           'passing them as args to sequences and functions'),
          emit_tests.sequence_plus_externals_tests.run_test),

        ('Emit test basic endpoint calls',
         emit_tests.basic_endpoint_call_test.run_test),

        ('Emit test user struct setup',
         emit_tests.user_struct_basics.run_test),

        ('Emit test for single side onCreate',
         emit_tests.oncreate_single_node_test.run_test),

        ('Emit test two sided onCreate',
         emit_tests.two_sided_oncreate_test.run_test),

        ('Emit test TCP connection test peered data',
         emit_tests.network_two_sided_modify_peer_check_update_test.run_test),

        ('Test self with onCreate append to external list',
         emit_tests.self_oncreate_list.run_test),

        ('Test create externals inside of Waldo',
         emit_tests.create_externals_inside_waldo.run_test),

        ('Test loading self into external maps and lists',
         emit_tests.external_reference_tests.run_test),

        ('Test basic function objects',
         emit_tests.function_obj_test.run_test),

        ('Test user struct as library',
         emit_tests.user_struct_as_library_test.run_test),
        
        ]

    run_tests(emit_tests_to_run)
    

def run_all():
    run_lib_tests()
    run_emit_tests()

if __name__ == '__main__':
    run_all()
