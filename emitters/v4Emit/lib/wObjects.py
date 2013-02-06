
from waldoObjBase import _WaldoObj

def initialize():
    '''
    Add separate type names to overall Waldo object.
    '''
    _WaldoObj.WALDO_TYPE_NAMES[WaldoNum.TYPE_WALDO_NUM] = True
    # _WaldoObj.WALDO_TYPE_NAMES[_WaldoTrueFalse.TYPE_WALDO_TF] = True
    # _WaldoObj.WALDO_TYPE_NAMES[_WaldoText.TYPE_WALDO_TEXT] = True
    # _WaldoObj.WALDO_TYPE_NAMES[_WaldoList.TYPE_WALDO_LIST] = True
    # _WaldoObj.WALDO_TYPE_NAMES[_WaldoMap.TYPE_WALDO_MAP] = True

        

class WaldoNum(_WaldoObj):
    TYPE_WALDO_NUM = 'number'

    def __init__(self,init_val=0):
        _WaldoObj.__init__(self,WaldoNum.TYPE_WALDO_NUM,init_val)
        

        
