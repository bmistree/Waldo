
from waldoObjBase import _WaldoObj

def initialize():
    '''
    Add separate type names to overall Waldo object.
    '''
    _WaldoObj.WALDO_TYPE_NAMES[WaldoNum.TYPE_WALDO_NUM] = True
    _WaldoObj.WALDO_TYPE_NAMES[
        WaldoTrueFalse.TYPE_WALDO_TRUE_FALSE] = True
    _WaldoObj.WALDO_TYPE_NAMES[WaldoText.TYPE_WALDO_TEXT] = True
    # _WaldoObj.WALDO_TYPE_NAMES[WaldoList.TYPE_WALDO_LIST] = True
    # _WaldoObj.WALDO_TYPE_NAMES[WaldoMap.TYPE_WALDO_MAP] = True

        

### VALUE TYPES
    
class WaldoNum(_WaldoObj):
    TYPE_WALDO_NUM = 'number'

    def __init__(self,init_val=0):
        _WaldoObj.__init__(self,WaldoNum.TYPE_WALDO_NUM,init_val)

        
class WaldoText(_WaldoObj):
    TYPE_WALDO_TEXT = 'text'
    
    def __init__(self,init_val=''):
        _WaldoObj.__init__(self,WaldoText.TYPE_WALDO_TEXT,init_val)
        
        
class WaldoTrueFalse(_WaldoObj):
    TYPE_WALDO_TRUE_FALSE = 'tf'
    
    def __init__(self,init_val=False):
        _WaldoObj.__init__(self,WaldoTrueFalse.TYPE_WALDO_TRUE_FALSE,init_val)