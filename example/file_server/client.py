#!/usr/bin/env python

from emitted import Client
from server import PORT_NO, HOST_NAME

import re
import os
import sys
import time

proj_root_folder = os.path.join(os.path.dirname(__file__),'..','..')
sys.path.append(proj_root_folder)
import lib.Waldo as Waldo


def written_callback(filename,contents):
    print '\nClient has written \n'
    print contents
    print '\nto file ' + filename + '\n'
    
def run():

    Waldo.initialize()
    
    # try to bind to HOST_NAME:PORT_NO when creating client
    client = Waldo.connect(
        connection_type = Waldo.CONNECTION_TYPE_TCP,
        host_name = HOST_NAME,
        port = PORT_NO,
        constructor = Client)


    while True:
        # event loop to grab user input        
        print '\nTo load contents into a file, use ',
        print 'write "<filename>" "<contents to write>".'
        print 'To read contents from file, use ',
        print 'read "<filename>".  To remove a file, ',
        print 'use remove "<filename>"\n'
        
        
        user_input = raw_input ('-->')

        action,filename,contents = parse_user_input(user_input)

        print '\n\n'            
        if action == 'read':
            str_returned = client.get(filename,'')
            print 'Got back: "' + str_returned + '"'
        elif action == 'write':
            client.write(filename,contents)
            print 'Contents have been written.'
        elif action == 'remove':
            client.delete_file(filename)
            print 'Contents have been removed.'
        else:
            print 'Invalid action selected.  Try again.'
            
        print '\n\n'


def parse_user_input(user_input):
    '''
    Either:
       write "<filename>" "<contents to write>"
    or
       read "<filename>"
    or
       remove "<filename>"

    In first case, returns 3-tuple: 'write', <filename>, <contents to
    write>

    In second case, returns 3-tuple: 'read',<filename>,None

    Otherwise, returns 3-tuple: None,None,None
    '''
    space_index = user_input.find(' ')
    if space_index == -1:
        return None,None,None
    action = user_input[0:space_index]

    if not (action in ['read','write','remove']):
        return None,None,None
    
    user_input = user_input[space_index + 1:]

    quote_regexp = '\"(.*?)\"'
    all_quotes = re.findall(quote_regexp,user_input)

    filename = None
    file_contents = None
    if len(all_quotes) > 0:
        filename = all_quotes[0]
    if len(all_quotes) > 1:
        file_contents = all_quotes[1]
        
    return action,filename,file_contents
    

    

if __name__ == '__main__':
    run();

