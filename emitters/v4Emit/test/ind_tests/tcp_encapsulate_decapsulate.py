#!/usr/bin/env python

import os, sys, random
sys.path.append(
    os.path.join('../../lib/'))
import waldoConnectionObj

NUM_RANDOM_STRINGS = 2000
MAX_RAND_STRING_LEN = 5000


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


def run_test():
    strings_to_test = get_string_list_to_test()
    for counter in range(0, len(strings_to_test)):
        
        string = strings_to_test[counter]
        encapsulated = waldoConnectionObj._WaldoTCPConnectionObj._encapsulate_msg_str(string)
        decapsulated,rest_of_str = waldoConnectionObj._WaldoTCPConnectionObj._decapsulate_msg_str(encapsulated)

        if decapsulated != string:
            filer = open('faulty.txt','w')
            filer.write(string)
            filer.flush()
            filer.close()

            err_msg = '\nErr: cannot encapsulate and decapsulate '
            err_msg += 'string correctly.  Wrote faulty strin to file '
            err_msg += 'faulty.txt\n'
            print err_msg
            return False
    return True

# def run_test():
#     faulty_file = open('faulty.txt','r')
#     faulty_str = faulty_file.read()
#     encapsulated = waldoConnectionObj._WaldoTCPConnectionObj._encapsulate_msg_str(faulty_str)
#     decapsulated,rest_of_str = waldoConnectionObj._WaldoTCPConnectionObj._decapsulate_msg_str(encapsulated)
#     if decapsulated != faulty_str:
#         print '\nGotcha!\n'
    
    



if __name__ == '__main__':
    run_test()

