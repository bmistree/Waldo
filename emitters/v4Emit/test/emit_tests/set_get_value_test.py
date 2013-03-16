#!/usr/bin/env python

from set_get_val_wld_v4 import SingleSide


'''
Tests that can set endpoint global data and change endpoint global
data.  Without initialization of values.
'''

def run_test():
    # for single side tests, these values do not really matter.
    host_uuid = 10
    conn_obj = None
    single_side = SingleSide(host_uuid,conn_obj)

    if single_side.get_num() != 0:
        print '\nGot incorrect initial value for number'
        return False

    if single_side.get_txt() != '':
        print '\nGot incorrect initial value for text'
        return False

    for counter in range(0,100):
        if single_side.increment_num() != counter + 1:
            print '\nGot incorrect number when incrementing'
            return False

        # just want to append a single a each time.  Note: probably
        # more efficient to just keep track of a shadow text val
        # myself and append an 'a' to it each time.  But I wanted to
        # play with reduce a bit.
        expected_str = reduce(
            lambda x,y: x + y,            
            (['a']*(counter+1)),
            '')

        if single_side.increment_txt('a') != expected_str:
            print '\nGot incorrect string back'
            return False


        internal_list = single_side.increment_list(counter)
        expected_internal_list = list(range(0,counter+1))
        if internal_list != expected_internal_list:
            print '\nNot appending to internal list correctly'
            return False
            
    return True



if __name__ == '__main__':
    run_test()