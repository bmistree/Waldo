#!/usr/bin/env python
import os,sys,time
sys.path.append(
    os.path.join('..','..'))
from lib import Waldo, util, WaldoFS


from single_file_v4 import Single


def run(test_filename,init_val):
    waldo_file = WaldoFS.WaldoExtFileVariable(test_filename,init_val)
    single = Waldo.no_partner_create(Single,waldo_file)
    time.sleep(10)
    single.write_into_file('ooo bla')
    time.sleep(10)
    
    
if __name__ == '__main__':
    run(sys.argv[1],sys.argv[2])
