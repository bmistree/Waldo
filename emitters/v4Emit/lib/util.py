import uuid


def generate_uuid():
    return uuid.uuid4()


def logger_assert(assert_msg):
    print 'Behram error: ' + assert_msg
    assert(False)
    
