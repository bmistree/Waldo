package waldo;

import waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas;
import waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas.ContainerAction.ContainerAddedKey;
import waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas.ContainerAction.ContainerWriteKey;
import waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas.SingleInternalMapDelta;
import waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas.SingleListDelta;
import waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas.SingleMapDelta;
import waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas.SubElementUpdateActions;
import java.util.HashMap;


/**
 * 
 * @author bmistree
 *
 * @param <K> --- Keys for the container (Can be Numbers, Booleans, or Strings).
 * @param <V> --- The Java type of data that the keys should point to.
 * @param <D> --- The Java type of data that the internal locked objects should dewaldoify into
 */
public class SingleThreadedLockedContainer<K,V,D> 
     extends SingleThreadedLockedObject <
     				// The internal values that these are holding
     				HashMap<K,LockedObject<V,D>>,
				    // When call dewaldoify on this container, what we should get back
				    HashMap<K,D>
				    >  
     //implements ContainerInterface<K,V>
{

	@Override
	public HashMap<K, LockedObject<V,D>> get_val(LockedActiveEvent active_event)
    {
    	Util.logger_assert("Cannot call get val on a container object.");
    	return null;
    }
    
    @Override
    public void set_val(LockedActiveEvent active_event, HashMap<K,LockedObject<V,D>> val_to_set_to)
    {
    	Util.logger_assert("Cannot call set val on a container object directly.");
    }

	@Override
	public void write_if_different(LockedActiveEvent active_event,
			HashMap<K, LockedObject<V,D>> new_val) {
		// should only call this method on a value type
		Util.logger_assert("Unable to call write if different on container");
		
	}
  
	@Override
    public boolean serializable_var_tuple_for_network (
    		VarStoreDeltas.Builder parent_delta,String var_name, LockedActiveEvent active_event,boolean force)
    {
		SingleMapDelta.Builder single_map_delta = create_internal_map_delta(var_name,active_event,force);
		if (single_map_delta != null)
			parent_delta.addMapDeltas(single_map_delta);
    	
        return single_map_delta != null;
    }

	/**
	 * Same parameters as serializable_var_tuple_for_network
	 * @return --- null if no subtree has been written and we aren't being forced to create a builder
	 */
	private SingleMapDelta.Builder create_internal_map_delta(String var_name, LockedActiveEvent active_event, boolean force)
	{
    	boolean has_been_written_since_last_msg = get_and_reset_has_been_written_since_last_msg(active_event);
    	
    	// Just doing maps for now
    	SingleMapDelta.Builder single_map_delta = SingleMapDelta.newBuilder();
    	
    	
    	single_map_delta.setVarName(var_name);
    	single_map_delta.setHasBeenWritten(has_been_written_since_last_msg);
    	
    	// check if any sub elements of the map have also been written
    	boolean internal_has_been_written = 
    			internal_container_variable_serialize_var_tuple_for_network(
    					single_map_delta,var_name,active_event,
    			        // must force the write when we have written a new value over list
    					force || has_been_written_since_last_msg);
    	
    	// only add the delta if a subelement has changed or we're being forced
    	if (internal_has_been_written || has_been_written_since_last_msg || force)
    		return single_map_delta;
    	return null;
	}
    
    /**
     * 
     * @param single_map_delta
     * @param var_name
     * @param active_event
     * @param force
     * @return --- True if subelement of map has been modified (ie, we need to
     *  serialize and send this branch of the map to the other side).  False otherwise.
     */
	private boolean internal_container_variable_serialize_var_tuple_for_network(
			SingleMapDelta.Builder single_map_delta, String var_name,
			LockedActiveEvent active_event, boolean force) 
	{
		
		// var_data = locked_container.val.val
		HashMap<K,LockedObject<V,D>> var_data = val.val;
		
		// FIXME: If going to have publicly peered data, need to use
	    // locked_container.dirty_val instead of locked_container.val when
	    // incorporating changes???  .get_dirty_wrapped_val returns
	    // wrapped val that can use for serializing data.

		ReferenceTypeDataWrapper <K,V,D> dirty_wrapped_val = get_dirty_wrapped_val(active_event);
		boolean sub_element_modified = false;
		
		SingleInternalMapDelta.Builder internal_map_delta = SingleInternalMapDelta.newBuilder();
		internal_map_delta.setParentType(VarStoreDeltas.ParentType.INTERNAL_MAP_CONTAINER);
		single_map_delta.setInternalMapDelta(internal_map_delta);
		if (force)
		{
			// for each item in map, add it to delta as a write action.
			dirty_wrapped_val.add_all_data_to_delta_list(internal_map_delta, var_data, active_event, true);
			sub_element_modified = true;
		}
		else
		{
			//# if all subelements have not been modified, then we
			//# do not need to keep track of these changes.
			//# wVariable.waldoMap, wVariable.waldoList, or
			//# wVariable.WaldoUserStruct will get rid of it later.
			sub_element_modified = dirty_wrapped_val.add_to_delta_list(
					internal_map_delta, var_data, active_event, true);
		}
		return sub_element_modified;
	}
			
	
/*

	@Override
	public boolean serializable_var_tuple_for_network(VarStoreDeltas.Builder parent_delta,
			String var_name, LockedActiveEvent active_event, boolean force) {
		// TODO Auto-generated method stub
		return false;
	}
*/
	@Override
	public boolean serializable_var_tuple_for_network(
			SingleListDelta.Builder parent_delta,
			String var_name, LockedActiveEvent active_event, boolean force) {
		// TODO Auto-generated method stub
		return false;
	}

	@Override
	public boolean serializable_var_tuple_for_network(
			SingleMapDelta.Builder parent_delta,
			String var_name, LockedActiveEvent active_event, boolean force) {
		// TODO Auto-generated method stub
		return false;
	}

	@Override
	public boolean serializable_var_tuple_for_network(
			ContainerAddedKey.Builder parent_delta,
			String var_name, LockedActiveEvent active_event, boolean force) {
		// TODO Auto-generated method stub
		return false;
	}

	@Override
	public boolean serializable_var_tuple_for_network(
			SubElementUpdateActions.Builder parent_delta,
			String var_name, LockedActiveEvent active_event, boolean force) {
		// TODO Auto-generated method stub
		return false;
	}

	@Override
	public boolean serializable_var_tuple_for_network(
			ContainerWriteKey.Builder parent_delta,
			String var_name, LockedActiveEvent active_event, boolean force) {
		// TODO Auto-generated method stub
		return false;
	}

	public ReferenceTypeDataWrapper<K,V,D> get_dirty_wrapped_val(LockedActiveEvent active_event)
	{
		// TODO Auto-generated method stub
		return null;
	}
	

}
