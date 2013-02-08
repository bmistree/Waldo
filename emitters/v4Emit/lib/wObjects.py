
from waldoObjBase import _WaldoObj
from waldoObjBase import _ValueTypeVersion
from waldoObjBase import _ValueDirtyMapElement

from waldoContainerBase import _WaldoValueContainer
from waldoContainerBase import _ContainerValueTypeVersion
from waldoContainerBase import _ValueContainerDirtyMapElement


def initialize():
    '''
    Add separate type names to overall Waldo object.
    '''
    _WaldoObj.WALDO_TYPE_NAMES[WaldoNum.TYPE_WALDO_NUM] = True
    _WaldoObj.WALDO_TYPE_NAMES[
        WaldoTrueFalse.TYPE_WALDO_TRUE_FALSE] = True
    _WaldoObj.WALDO_TYPE_NAMES[WaldoText.TYPE_WALDO_TEXT] = True
    _WaldoObj.WALDO_TYPE_NAMES[WaldoValueMap.TYPE_WALDO_VALUE_MAP] = True    
    # _WaldoObj.WALDO_TYPE_NAMES[WaldoList.TYPE_WALDO_LIST] = True


        

### VALUE TYPES
    
class WaldoNum(_WaldoObj):
    TYPE_WALDO_NUM = 'number'

    def __init__(self,init_val=0):
        _WaldoObj.__init__(
            self,WaldoNum.TYPE_WALDO_NUM,init_val,
            _ValueTypeVersion(),_ValueDirtyMapElement)

    
class WaldoText(_WaldoObj):
    TYPE_WALDO_TEXT = 'text'
    
    def __init__(self,init_val=''):
        _WaldoObj.__init__(
            self,WaldoText.TYPE_WALDO_TEXT,init_val,
            _ValueTypeVersion(),_ValueDirtyMapElement)

        
class WaldoTrueFalse(_WaldoObj):
    TYPE_WALDO_TRUE_FALSE = 'tf'
    
    def __init__(self,init_val=False):
        _WaldoObj.__init__(
            self,WaldoTrueFalse.TYPE_WALDO_TRUE_FALSE,init_val,
            _ValueTypeVersion(),_ValueDirtyMapElement)

class WaldoValueMap(_WaldoValueContainer):
    TYPE_WALDO_VALUE_MAP = 'value map'
    
    def __init__(self,init_val=None):
        if init_val == None:
            init_val = {}
            
        _WaldoValueContainer.__init__(
            self,WaldoValueMap.TYPE_WALDO_VALUE_MAP,init_val,
            _ContainerValueTypeVersion(),_ValueContainerDirtyMapElement)
