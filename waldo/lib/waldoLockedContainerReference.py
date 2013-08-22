from waldo.lib.waldoLockedValueVariablesHelper import SingleThreadedLockedValueVariable
from waldo.lib.waldoLockedValueVariablesHelper import LockedValueVariable

'''
All reference variables (lists, maps, structs), inherit from these.
That is because need to use special methods to serialize and
deserialize them to send changes over the network.
'''


def serializable_var_tuple_for_network(ref_obj,parent_delta,var_name,active_event,force):
    var_data = ref_obj.get_val(active_event)
    return var_data.serializable_var_tuple_for_network(
            parent_delta,var_name,active_event,force)

def incorporate_deltas(ref_obj,delta_to_incorporate,constructors,active_event):
    # FIXME: when allow peered data, will have to clean this up.
    internal_container = ref_obj.get_val(active_event)
    internal_container.incorporate_deltas(delta_to_incorporate,constructors,active_event)

def de_waldoify(self,active_event):
    return self.get_val(active_event).de_waldoify(active_event)
    
class MultiThreadedContainerReference(LockedValueVariable):
    def serializable_var_tuple_for_network(self,parent_delta,var_name,active_event,force):
        return serializable_var_tuple_for_network(
            self,parent_delta,var_name,active_event,force)
        
    def incorporate_deltas(self,delta_to_incorporate,constructors,active_event):
        return incorporate_deltas(self,delta_to_incorporate,constructors,active_event)

    def de_waldoify(self,active_event):
        return de_waldoify(self,active_event)
        
class SingleThreadedContainerReference(SingleThreadedLockedValueVariable):
    def serializable_var_tuple_for_network(self,parent_delta,var_name,active_event,force):
        return serializable_var_tuple_for_network(
            self,parent_delta,var_name,active_event,force)
        
    def incorporate_deltas(self,delta_to_incorporate,constructors,active_event):
        return incorporate_deltas(self,delta_to_incorporate,constructors,active_event)

    def de_waldoify(self,active_event):
        return de_waldoify(self,active_event)
