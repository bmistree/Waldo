from Waldo import _host_uuid

from pysnmp.entity.rfc3413.oneliner import cmdgen,mibvar
from pysnmp.proto.rfc1902 import Integer
from waldoInternalMap import InternalMap, _InternalMapVersion, _InternalMapDirtyMapElement
import waldoReferenceContainerBase
from wVariables import WaldoMapVariable, _WaldoVariable
from Waldo import _host_uuid
from waldoReferenceContainerBase import write_key_tuple, is_write_key_tuple

# pip install pysnmp

'''
The model here is that you create an ext snmp map.  Its internal value
is a regular internal map.  Whenever you complete a commit on the snmp
number map variable, you run through changes to internal value and
commit them.
'''
class SNMPExtNumberMapVar(WaldoMapVariable):
    def __init__(self,other_end_host,other_end_port,key_list):
        internal_map = _SNMPNumberInternalMap(
            _host_uuid,other_end_host,other_end_port,key_list)
        _WaldoVariable.__init__(self,'',_host_uuid,False,internal_map)


class _SNMPNumberInternalMap(InternalMap):
    
    def __init__(self,host_uuid,other_end_host,other_end_port,key_list):
        self.other_end_host = other_end_host
        self.other_end_port = other_end_port

        # collect original snmp values
        init_val = self.grab_snmps(key_list)
        
        waldoReferenceContainerBase._ReferenceContainer.__init__(
            self,host_uuid,False,init_val,_InternalMapVersion(),
            _InternalMapDirtyMapElement)

    def grab_snmps(self,key_list):
        '''
        @param {list} key_list --- each item is a text string of the
        fully qualified object id.  Eg., '1.3.6.1.4.1.44.1.0'.
        '''
        map_init_val = {}
        for key in key_list:
            val = self.get_integer_var(key)
            map_init_val[key] = val

        return map_init_val

    def _add_invalid_listener(self,invalid_listener):
        '''
        ASSUMES ALREADY WITHIN LOCK

        Biggest difference between this version and base class'
        version of _add_invalid_listener is that this version adds a
        touch to invalid listener with high priority.  Other classes
        use low priority.  Want to ensure that can commit this before
        commit any of the individual numbers.
        '''
        if invalid_listener.uuid not in self._dirty_map:
            
            # FIXME: may only want to make a copy of val on write
            to_add = self.dirty_element_constructor(
                self.version_obj.copy(),
                self.val,
                invalid_listener,self)

            self._dirty_map[invalid_listener.uuid] = to_add

            invalid_listener.add_touch(self,True)

    def send_snmp_commands(self,change_commands,internal_dirty_element):
        '''
        @param {Array} change_commands --- Each is an individual add,
        delete, or write key tuple.

        Run through array and issue each command separately.
        '''
        for cmd in change_commands:
            if is_write_key_tuple(cmd):
                key = cmd[1]
                new_val = internal_dirty_element.val[key]
                self.set_integer_var(key,new_val)
            else:
                util.logger_assert(
                    'SNMP delete or append are currently unsupported')

    def complete_commit(self,invalid_listener):
        # the fields within the map got changed.  The changes to these
        # fields should be sent and updated. gather modifications
            
        # send all modifications
        internal_map_dirty_element = self._dirty_map[invalid_listener.uuid]
        num_dict = internal_map_dirty_element.val
        num_dict_version_obj = internal_map_dirty_element.version_obj
            
        # each of these correspond to a change made to the version object
        change_commands = num_dict_version_obj.partner_change_log

        # run through each command and send it, via snmp to
        # listening device
        self.send_snmp_commands(change_commands,internal_map_dirty_element)
        super(_SNMPNumberInternalMap,self).complete_commit(invalid_listener)

        

    def get_integer_var(self,key):
        cmdGen = cmdgen.CommandGenerator()
        community_data = cmdgen.CommunityData('public')
        errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(
            cmdgen.CommunityData('public'),
            cmdgen.UdpTransportTarget((self.other_end_host, self.other_end_port)),
            key)

        # Check for errors and print out results
        if errorIndication:
            print(errorIndication)
        else:
            if errorStatus:
                print('%s at %s' % (
                    errorStatus.prettyPrint(),
                    errorIndex and varBinds[int(errorIndex)-1] or '?'
                    )
                )
            else:
                for name, val in varBinds:
                    return val._value

        
    def set_integer_var(self,val_key,val_to_set_to):
        cmdGen = cmdgen.CommandGenerator()
        errorIndication, errorStatus, errorIndex, varBinds = cmdGen.setCmd(
            cmdgen.CommunityData('public'),
            cmdgen.UdpTransportTarget((self.other_end_host, self.other_end_port)),
            (val_key,Integer(val_to_set_to)))

        # Check for errors and print out results
        if errorIndication:
            print(errorIndication)
        else:
            if errorStatus:
                print('%s at %s' % (
                    errorStatus.prettyPrint(),
                    errorIndex and varBinds[int(errorIndex)-1] or '?'
                    )
                )
        

