#!/usr/bin/env python

import os, sys, random
sys.path.append(
    os.path.join('../../lib/'))
import waldoConnectionObj

NUM_RANDOM_STRINGS = 2000
NUM_MULTI_MESSAGES = 500
MAX_RAND_STRING_LEN = 5000
MAX_NUM_IN_MULTI_MESSAGE = 10

def get_random_string():
    string = ''
    rand_str_len = random.randint(0,MAX_RAND_STRING_LEN)
    for i in range(0,rand_str_len):
        LARGEST_CHAR_INT = 128
        rand_char_int = random.randint(0,LARGEST_CHAR_INT -1)
        string += str(unichr(rand_char_int))
    return string
    
def get_string_list_to_test():
    '''
    @returns {list} --- Each element is a string that we try to encapsulate and decapsulate
    '''
    to_return = []
    
    # put a bunch of random data in string list
    for i in range(0,NUM_RANDOM_STRINGS):
        rand_string = get_random_string()
        to_return.append(rand_string)

    return to_return


def decapsulate_all(to_decapsulate):
    rest_of_str = 'a'
    full_decapsulated = ''
    while rest_of_str != '':
        decapsulated,rest_of_str = waldoConnectionObj._WaldoTCPConnectionObj._decapsulate_msg_str(to_decapsulate)
        full_decapsulated += decapsulated
        to_decapsulate = rest_of_str

    return full_decapsulated

    print counter

def check_err(decapsulated,original):
    '''
    @returns{bool} --- True if there is an error, False otherwise.
    '''
    if decapsulated != original:
        filer = open('faulty.txt','w')
        filer.write(original)
        filer.flush()
        filer.close()

        err_msg = '\nErr: cannot encapsulate and decapsulate '
        err_msg += 'string correctly.  Wrote faulty string to file '
        err_msg += 'faulty.txt\n'
        print err_msg
        return True
    return False


def run_test():
    strings_to_test = get_string_list_to_test()
    for counter in range(0, len(strings_to_test)):
        string = strings_to_test[counter]
        encapsulated = waldoConnectionObj._WaldoTCPConnectionObj._encapsulate_msg_str(string)
        decapsulated = decapsulate_all(encapsulated)

        if check_err(decapsulated, string):
            return False


    for i in range(0,NUM_MULTI_MESSAGES ):
        num_concatenated_msgs = random.randint(1,MAX_NUM_IN_MULTI_MESSAGE)
        expected_deserialized_msg = ''
        serialized_msg = ''

        # construct a message of many serialized strings
        for j in range(0,num_concatenated_msgs):
            single_string_index = random.randint(1,len(strings_to_test)) - 1
            single_string = strings_to_test[single_string_index]
            expected_deserialized_msg += single_string
            serialized_msg += waldoConnectionObj._WaldoTCPConnectionObj._encapsulate_msg_str(
                single_string)

        
        decapsulated = decapsulate_all(serialized_msg)
        if check_err(decapsulated,expected_deserialized_msg):
            return False
        
    return True


if __name__ == '__main__':
    run_test()

