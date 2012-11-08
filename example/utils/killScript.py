#!/usr/bin/env python

import subprocess;
import re;
import sys;

'''
Written as a utility to simplify killing python programs that are
multi-threaded.  Just set the name of your script as SCRIPT_NAME and
USER_NAME as the user that is running the script.  
'''

DEFAULT_SCRIPT_BASE = 'python '
DEFAULT_SCRIPT_NAME = DEFAULT_SCRIPT_BASE + './test.py'
USER_NAME = 'bmistree';


def run(script_name):
    '''
    Searches through all active processes for the one that matches the
    username and script name functions.  Then asks user if wants to
    kill it.
    '''
    cmd = ['ps','aux'];
    proc = subprocess.Popen(cmd,stdout=subprocess.PIPE);
    proc.wait();

    procRegExp = USER_NAME + '\s+(\d+).*?'+ script_name + '$';
    for procLine in proc.stdout:
        
        foundItems = re.findall(procRegExp,procLine);

        if len(foundItems) == 1:
            questionString = '\n';
            questionString += 'Delete    ' + procLine + '\n';
            questionString += '[y/n]:   ';
            userInput = raw_input(questionString);
            
            if userInput.lstrip().rstrip() == 'y':
                killIt (int(foundItems[0]));
                return;

        elif len(foundItems) != 0:
            # don't really know what to do if had multiple matches to
            # regexp.  do conservative thing and just print error
            # message and quit.
            print('\n\nToo many matches.  Abandoning.\n');
            print(procLine);
            print(foundItems);
            print('\n\n');
            assert(False);


def killIt(procIdToKill):
    '''
    @param {int} procIdToKill --- The id of the process to kill.

    Actually executes the kill function for you.
    '''
    cmd = ['kill' , str(procIdToKill)];
    proc = subprocess.Popen(cmd);
    proc.wait();
            

if __name__ == '__main__':
    if len(sys.argv) == 2:
        run(DEFAULT_SCRIPT_BASE + sys.argv[1]);
    else:
        run(DEFAULT_SCRIPT_NAME)
