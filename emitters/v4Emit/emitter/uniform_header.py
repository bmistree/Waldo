

def uniform_header():
    '''
    Every Waldo file starts the same way (imports the same files, has
    the same comments, etc.).  This function returns the default
    starting string for the file.
    '''

    return '''
# Waldo emitted file


'''.lstrip()
