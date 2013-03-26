from math_endpoint_v4 import MathEndpoint 


def min_func(endpoint,num_list):
    return min(num_list)

def max_func(endpoint,num_list):
    return max(num_list)

def mod_func(endpoint,lhs,rhs):
    return lhs % rhs



_math_endpoint = None

# FIXME: not threadsfe

def math_endpoint(no_partner_create):
    '''
    @param {Function} no_partner_create --- Waldo.no_partner_create
    function.
    '''
    global _math_endpoint
    if _math_endpoint == None: 
        _math_endpoint = no_partner_create(
            MathEndpoint,min_func,max_func,mod_func)
    
    return _math_endpoint
    



