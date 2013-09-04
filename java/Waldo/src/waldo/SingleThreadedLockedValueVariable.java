package waldo;

import com.google.protobuf.Message.Builder;

import waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas;


public abstract class SingleThreadedLockedValueVariable<T> extends SingleThreadedLockedObject<T>
{
	public SingleThreadedLockedValueVariable(String _host_uuid, boolean _peered,
			T init_val, T DEFAULT_VALUE, ValueTypeDataWrapperConstructor<T> vtdwc)
	{
		if (init_val == null)
			init_val = DEFAULT_VALUE;
		init(vtdwc,_host_uuid,_peered,init_val);
	}

	
	public void write_if_different(LockedActiveEvent active_event,T data)
	{
		val.write(data,true);
	}
	
	public boolean return_internal_val_from_container()
	{
		return true;
	}

	
            
	@Override
	/**
	 *   @see waldoLockedObj.serializable_var_tuple_for_network
	 */
	public boolean serializable_var_tuple_for_network(
		VarStoreDeltas.Builder parent_delta, String var_name, LockedActiveEvent active_event, boolean force) 
    {
		return _serializable_var_tuple_for_network(parent_delta,var_name,active_event,force);
	}
	@Override
	public boolean serializable_var_tuple_for_network(
			waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas.ContainerAction.ContainerAddedKey.Builder parent_delta,
			String var_name, LockedActiveEvent active_event, boolean force) 
	{
		return _serializable_var_tuple_for_network(parent_delta,var_name,active_event,force);
	}

	@Override
	public boolean serializable_var_tuple_for_network(
			waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas.ContainerAction.ContainerWriteKey.Builder parent_delta,
			String var_name, LockedActiveEvent active_event, boolean force) 
	{
		return _serializable_var_tuple_for_network(parent_delta, var_name, active_event,force);
	}

	
	
	/**
	 * Each, individual subclassed singlethreadedlockedvariable will override value_variable_py_val_serialize for its target type.
	 * @param parent_delta
	 * @param var_name
	 * @param active_event
	 * @param force
	 * @return
	 */
	private boolean _serializable_var_tuple_for_network(
		Builder parent_delta,String var_name, LockedActiveEvent active_event, boolean force)
	{
        T var_data = get_val(active_event);
        boolean has_been_written_since_last_msg = get_and_reset_has_been_written_since_last_msg(active_event);
            
        if ((! force) && (! has_been_written_since_last_msg))
            return false;

        if (! value_variable_py_val_serialize(parent_delta,var_data,var_name))
        	Util.logger_assert("Failed serialization in value variable");
        return true;		
	}
	
    protected abstract boolean value_variable_py_val_serialize(VarStoreDeltas.Builder parent_delta,T var_data,String var_name);
    protected abstract boolean value_variable_py_val_serialize(waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas.ContainerAction.ContainerAddedKey.Builder parent_delta,T var_data,String var_name);
    protected abstract boolean value_variable_py_val_serialize(waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas.ContainerAction.ContainerWriteKey.Builder parent_delta,T var_data,String var_name);
    private boolean value_variable_py_val_serialize(Builder parent_delta,T var_data,String var_name)
    {
    	Util.logger_assert("Unknown builder type");
    	return false;
    }


    

	
	/** Useless serializable-s: value type variable should never encouter these**/
	@Override
	public boolean serializable_var_tuple_for_network(
			waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas.SingleListDelta.Builder parent_delta,
			String var_name, LockedActiveEvent active_event, boolean force) {
		Util.logger_assert("Should never have a parent delta of list in value type");
		return false;
	}

	@Override
	public boolean serializable_var_tuple_for_network(
			waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas.SingleMapDelta.Builder parent_delta,
			String var_name, LockedActiveEvent active_event, boolean force) {
		Util.logger_assert("Should never have a parent delta of map in value type");
		return false;
	}
	@Override
	public boolean serializable_var_tuple_for_network(
			waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas.SubElementUpdateActions.Builder parent_delta,
			String var_name, LockedActiveEvent active_event, boolean force) {
		Util.logger_assert("Should never have sub element update in value variable");
		return false;
	}

	
}
