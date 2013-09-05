package waldo;


import waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas;
import waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas.Builder;
import waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas.SingleListDelta;
import waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas.SingleMapDelta;
import waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas.SubElementUpdateActions;


public class SingleThreadedContainerReference <K,V,D> extends SingleThreadedLockedValueVariable< SingleThreadedLockedContainer<K,V,D>,D>
{
	public SingleThreadedContainerReference(String _host_uuid, boolean _peered, 
			SingleThreadedLockedContainer<K,V,D> init_val, SingleThreadedLockedContainer<K,V,D> default_value,
			ValueTypeDataWrapperConstructor< SingleThreadedLockedContainer<K,V,D>, D> vtdwc)
	{
		super(_host_uuid,_peered,init_val,default_value,vtdwc);
	}
	
	
	public D de_waldoify(LockedActiveEvent active_event)
	{
		return val.de_waldoify(active_event);
	}

	public boolean return_internal_val_from_container()
	{
		return false;
	}
	
	public void incorporate_deltas(SingleListDelta delta_to_incorporate, LockedActiveEvent active_event)
	{
		SingleThreadedLockedContainer<K,V,D> internal_container = get_val(active_event);
		internal_container.incorporate_deltas(delta_to_incorporate.getInternalListDelta(), active_event);
	}
	
	public void incorporate_deltas(SingleMapDelta delta_to_incorporate, LockedActiveEvent active_event)
	{
		SingleThreadedLockedContainer<K,V,D> internal_container = get_val(active_event);
		internal_container.incorporate_deltas(delta_to_incorporate.getInternalMapDelta(), active_event);
	}
        		
	@Override
	public boolean serializable_var_tuple_for_network(
			VarStoreDeltas.Builder parent_delta, String var_name, LockedActiveEvent active_event, boolean force) 
	{
		return get_val(active_event).serializable_var_tuple_for_network(parent_delta, var_name, active_event, force);
	}
	@Override
	public boolean serializable_var_tuple_for_network(
			waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas.ContainerAction.ContainerAddedKey.Builder parent_delta,
			String var_name, LockedActiveEvent active_event, boolean force) 
	{
		return get_val(active_event).serializable_var_tuple_for_network(parent_delta, var_name, active_event, force);
	}

	@Override
	public boolean serializable_var_tuple_for_network(
			waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas.ContainerAction.ContainerWriteKey.Builder parent_delta,
			String var_name, LockedActiveEvent active_event, boolean force) 
	{
		return get_val(active_event).serializable_var_tuple_for_network(parent_delta, var_name, active_event, force);
	}

	@Override
	public boolean serializable_var_tuple_for_network(
	        SingleListDelta.Builder parent_delta,String var_name,LockedActiveEvent active_event,boolean force)
	{
		return get_val(active_event).serializable_var_tuple_for_network(parent_delta, var_name, active_event, force);
	}
	@Override
	public boolean serializable_var_tuple_for_network(
	        SingleMapDelta.Builder parent_delta,String var_name,LockedActiveEvent active_event,boolean force)
	{
		return get_val(active_event).serializable_var_tuple_for_network(parent_delta, var_name, active_event, force);
	}
	@Override
	public boolean serializable_var_tuple_for_network(
			SubElementUpdateActions.Builder parent_delta,String var_name,LockedActiveEvent active_event,boolean force)
	{
		return get_val(active_event).serializable_var_tuple_for_network(parent_delta, var_name, active_event, force);
	}

	
	
	/** Dummy methods **/
	@Override
	protected boolean value_variable_py_val_serialize(Builder parent_delta,
			SingleThreadedLockedContainer<K, V, D> var_data, String var_name) 
	{
		Util.logger_assert("Should never py val serialize a container.");
		return false;
	}

	@Override
	protected boolean value_variable_py_val_serialize(
			waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas.ContainerAction.ContainerAddedKey.Builder parent_delta,
			SingleThreadedLockedContainer<K, V, D> var_data, String var_name) {
		Util.logger_assert("Should never py val serialize a container.");
		return false;
	}

	@Override
	protected boolean value_variable_py_val_serialize(
			waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas.ContainerAction.ContainerWriteKey.Builder parent_delta,
			SingleThreadedLockedContainer<K, V, D> var_data, String var_name) {
		Util.logger_assert("Should never py val serialize a container.");
		return false;
	}
        		
  }
