#!/usr/bin/env python

import os
import sys
import subprocess

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
import locked_tests.partner_seq_local_map_test
import locked_tests.partner_seq_local_list_test

emit_test_dir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), 'emit_tests')

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
        ('Sequence local map',locked_tests.partner_seq_local_map_test.run_test),
        ('Sequence local list',locked_tests.partner_seq_local_list_test.run_test),
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

    
def run_emit_tests():
    '''
    Must be run after 
    '''
    call_make_in_emit_test_folder()

    # use peered data
    # import emit_tests.two_sided_modify_peer_check_update_test
    # import emit_tests.sequence_local_data_tests
    # import emit_tests.basic_endpoint_call_test
    # import emit_tests.two_sided_oncreate_test
    # import emit_tests.network_two_sided_modify_peer_check_update_test
    # import emit_tests.basic_message_sequence_tests

    import emit_tests.set_get_value_test
    import emit_tests.binary_operator_tests
    import emit_tests.tuple_return_tests
    import emit_tests.single_endpoint_initialization_tests
    import emit_tests.signal_tests
    import emit_tests.conditional_tests
    import emit_tests.pass_references_through_methods
    import emit_tests.loop_tests
    import emit_tests.misc_tests
    import emit_tests.external_tests
    import emit_tests.sequence_plus_externals_tests
    import emit_tests.user_struct_basics
    import emit_tests.oncreate_single_node_test
    import emit_tests.self_oncreate_list
    import emit_tests.create_externals_inside_waldo
    import emit_tests.external_reference_tests
    import emit_tests.function_obj_test
    import emit_tests.user_struct_as_library_test
    import emit_tests.endpoint_as_library_test
    import emit_tests.symmetric_test
    import emit_tests.more_struct_tests
    import emit_tests.foreign_func_in_sequence
    import emit_tests.multiple_sequences
    import emit_tests.single_side_stop
    import emit_tests.two_side_stop
    import emit_tests.two_side_stop_callbacks
    import emit_tests.single_thread_references
    import emit_tests.self_type
    import emit_tests.id_method
    import emit_tests.retry_cb
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
    import emit_tests.retry_test
    
    
    emit_tests_to_run = [

        # No peered data
        # ('Emit test peered number gets automatically updated when one side writes to it',
        #  emit_tests.two_sided_modify_peer_check_update_test.run_test),

        # ('Emit test sequence local data tests',
        #  emit_tests.sequence_local_data_tests.run_test),

        # ('Emit test basic endpoint calls',
        #  emit_tests.basic_endpoint_call_test.run_test),

        # ('Emit test two sided onCreate',
        #  emit_tests.two_sided_oncreate_test.run_test),

        # ('Emit test TCP connection test peered data',
        #  emit_tests.network_two_sided_modify_peer_check_update_test.run_test),

        # ('Emit test update peered data across several sequence blocks',
        #  emit_tests.basic_message_sequence_tests.run_test),

        
        ('Emit test set endpoint value/get endpoint value',
         emit_tests.set_get_value_test.run_test),

        ('Emit test binary operators',
         emit_tests.binary_operator_tests.run_test),

        ('Emit test tuple returns',
         emit_tests.tuple_return_tests.run_test),

        ('Emit test endpoint and local var initialization',
         emit_tests.single_endpoint_initialization_tests.run_test),
        
        ('Tests signal code',
         emit_tests.signal_tests.run_test),
        
        ('Emit test conditional statements',
         emit_tests.conditional_tests.run_test),

        ('Emit test pass references through methods',
         emit_tests.pass_references_through_methods.run_test),
        
        ('Emit test loops',
         emit_tests.loop_tests.run_test),

        ('Emit test misc',
         emit_tests.misc_tests.run_test),

        ('Emit test externals',
         emit_tests.external_tests.run_test),

        ( ('Emit test coercing externals to value types when' +
           'passing them as args to sequences and functions'),
          emit_tests.sequence_plus_externals_tests.run_test),

        ('Emit test user struct setup',
         emit_tests.user_struct_basics.run_test),

        ('Emit test for single side onCreate',
         emit_tests.oncreate_single_node_test.run_test),

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

        ('Tests single side stop',
         emit_tests.single_side_stop.run_test),

        ('Tests to ensure stop message sent to other side',
          emit_tests.two_side_stop.run_test),

        ('Tests to ensure fires stop callbacks',
          emit_tests.two_side_stop_callbacks.run_test),

        ('Tests that can promote a singly-threaded list to being multithreaded',
         emit_tests.single_thread_references.run_test),

        ('Tests self type',
         emit_tests.self_type.run_test),
        
        ('Tests calling a foreign function in the midst of a sequence',
         emit_tests.foreign_func_in_sequence.run_test),

        ('Tests id method',
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

        # ('Tests network exception may be thrown in middle of a nested ' +
        #  'sequence and propagated back to be handled.',
        #  emit_tests.network_exception_nested_sequence_test.run_test),

        ('Tests retry callbacks',
         emit_tests.retry_cb.run_test),
        
        ('Tests try...finally statement (no use of catch).',
         emit_tests.try_finally_test.run_test),

        ('Tests vanilla retry',
         emit_tests.retry_test.run_test),
        
        ]

    run_tests(emit_tests_to_run)
    

def run_all():
    run_lib_tests()
    run_emit_tests()

if __name__ == '__main__':

    if len(sys.argv) == 1:
        run_all()
    else:
        flag = sys.argv[1]
        if flag == '-e':
            run_emit_tests()
        elif flag == '-l':
            run_lib_tests()
        else:
            print '\nUnknonw usage.\n'
