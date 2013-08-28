#!/usr/bin/env python

import os
import sys
import subprocess
sys.path.append(
    os.path.join('..','waldo','lib'))

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
import ind_tests.dd_wrapper
import ind_tests.test_de_waldoified
import ind_tests.tcp_encapsulate_decapsulate

emit_test_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), 'emit_tests')
security_test_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), 'security_tests')


def run_lib_tests():
    to_run = [
        ('Nested list', ind_tests.test_nested_list.run_test),
        ('Basic num test', ind_tests.test_num.run_test),
        ('List of values', ind_tests.test_value_list.run_test),
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
         ind_tests.dd_wrapper.run_test),

        ('Test tcp message encapsulation and decapsulation',
         ind_tests.tcp_encapsulate_decapsulate.run_test),
        
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


def call_make_in_emit_test_folder():
    cwd = os.getcwd()
    os.chdir(emit_test_dir)
    subprocess.call(['make','clean'])
    subprocess.call(['make','v4'])
    os.chdir(cwd)

def call_make_in_security_test_folder():
    cwd = os.getcwd()
    os.chdir(security_test_dir)
    subprocess.call(['make','clean'])
    subprocess.call(['make','v4'])
    os.chdir(cwd)

    
def run_emit_tests():
    '''
    Must be run after 
    '''
    call_make_in_emit_test_folder()
    call_make_in_security_test_folder()

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
    import emit_tests.endpoint_as_library_test
    import emit_tests.symmetric_test
    import emit_tests.more_struct_tests
    import emit_tests.multiple_sequences
    import emit_tests.signal_tests
    import emit_tests.single_side_stop
    import emit_tests.two_side_stop
    import emit_tests.two_side_stop_callbacks
    import emit_tests.single_thread_references
    import emit_tests.self_type
    import emit_tests.foreign_func_in_sequence
    import emit_tests.id_method

    # import security_tests.symmetric_test
    # import security_tests.symmetric_test_no_key
    import security_tests.two_side_stop


    import emit_tests.str_index_test
    import emit_tests.string_pass
    import emit_tests.application_exception_test
    import emit_tests.network_exception_mid_sequence_test
    import emit_tests.network_exception_on_call_test
    import emit_tests.network_exception_rollback_test
    import emit_tests.application_exception_endpoint_call_test
    import emit_tests.application_exception_sequence_propagate_test
    import emit_tests.network_exception_test_propagate_endpoint_call
    import emit_tests.application_exception_endpoint_call_with_sequence_test
    import emit_tests.application_exception_sequence_with_endpoint_call_test
    import emit_tests.application_exception_nested_sequence_test
    import emit_tests.network_exception_nested_sequence_test
    import emit_tests.try_finally_test

    
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

        ('Test endpoint as math library',
         emit_tests.endpoint_as_library_test.run_test),

        ('Test symmetric compile',
         emit_tests.symmetric_test.run_test),

        ('Stresses structs (passing them between partner endpoints, etc)',
         emit_tests.more_struct_tests.run_test),         

        ('Ensures that can run multiple sequences (in series) from one event',
         emit_tests.multiple_sequences.run_test),

        ('Tests signal code',
         emit_tests.signal_tests.run_test),

        ('Tests single side stop',
         emit_tests.single_side_stop.run_test),

        ('Tests to ensure stop message sent to other side',
          emit_tests.two_side_stop.run_test),

        ('Tests to ensure fires stop callbacks',
          emit_tests.two_side_stop_callbacks.run_test),

        ('Tests that can promote a singly-threaded list to being multithreaded',
         emit_tests.single_thread_references.run_test),

        ('Tests self type.',
         emit_tests.self_type.run_test),
        
        ('Tests calling a foreign function in the midst of a sequence',
         emit_tests.foreign_func_in_sequence.run_test),

        ('Tests id method.',
         emit_tests.id_method.run_test),
        
        ('Tests that you can get an index from a Text',
         emit_tests.str_index_test.run_test),
        
        ('Tests passing strings in a variety of ways',
         emit_tests.string_pass.run_test),

        ('Tests application exception may be thrown and caught.',
         emit_tests.application_exception_test.run_test),

        ('Tests network exception may be thrown mid-sequence due '
         'to socket closure and caught.',
         emit_tests.network_exception_mid_sequence_test.run_test),

        ('Tests network exception may be thrown at the beginning '
         'of a sequence due to prior network failure.',
         emit_tests.network_exception_on_call_test.run_test),

        ('Tests network exception which is properly caught does ' +
         'not back out of changes made during event.',
         emit_tests.network_exception_rollback_test.run_test),
    
        ('Tests application exception may be propagated back through ' +
         'endpoint call and caught.',
         emit_tests.application_exception_endpoint_call_test.run_test),

        ('Tests application exception may be propagated back across ' + 
         'endpoint connection mid-sequence and caught.',
         emit_tests.application_exception_sequence_propagate_test.run_test),

        ('Tests network exception may be propagated back through ' +
         'endpoint call and caught.',
         emit_tests.network_exception_test_propagate_endpoint_call.run_test),

        ('Tests application exception may be thrown on a remote endpoint ' + 
         'mid-sequence and propagated back through both a network connection ' +
         'and an endpoint call.',
         emit_tests.application_exception_endpoint_call_with_sequence_test.run_test),
        
        ('Tests application exception may be thrown on a remote endpoint ' + 
         'during an endpoint call invoked mid-sequence and propagated back to ' +
         'the root.',
         emit_tests.application_exception_sequence_with_endpoint_call_test.run_test),

        ('Tests application exception may be thrown on in the middle of a nested ' +
         'sequence and propagated back to be handled.',
         emit_tests.application_exception_nested_sequence_test.run_test),

    security_tests_to_run = [

        # ('Test secure symmetric compile',
        #  security_tests.symmetric_test.run_test),

        # ('Tests to ensure secure stop message sent to other side',
        #   security_tests.two_side_stop.run_test),

        # ('Test secure no key symmetric compile ',
        #  security_tests.symmetric_test_no_key.run_test),

        ]

        ('Tests network exception may be thrown in middle of a nested ' +
         'sequence and propagated back to be handled.',
         emit_tests.network_exception_nested_sequence_test.run_test),

        ('Tests try...finally statement (no use of catch).',
         emit_tests.try_finally_test.run_test),
        ]

    run_tests(emit_tests_to_run)
    run_tests(security_tests_to_run)
    
def clean_emit_test():
    cwd = os.getcwd()
    os.chdir(emit_test_dir)
    subprocess.call(['make','clean'])
    os.chdir(cwd)

def clean_security_test():
    cwd = os.getcwd()
    os.chdir(security_test_dir)
    subprocess.call(['make','clean'])
    os.chdir(cwd)

def clean_up():
    clean_emit_test()
    clean_security_test()
    

def run_all():
    run_lib_tests()
    run_emit_tests()
    clean_up()



if __name__ == '__main__':
    run_all()
