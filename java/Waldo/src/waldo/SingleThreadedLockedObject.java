package waldo;

import waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas;


public abstract class SingleThreadedLockedObject<T> extends LockedObject<T> {
	
	public String uuid = Util.generate_uuid();
	public String host_uuid = null;
	public boolean peered;
	private DataWrapperConstructor<T> data_wrapper_constructor;
	public DataWrapper<T,T> val = null;
	
	public SingleThreadedLockedObject(){}
	
	public void init(
			DataWrapperConstructor<T> dwc, String _host_uuid,boolean _peered, T init_val)
	{
		data_wrapper_constructor = dwc;
		host_uuid = _host_uuid;
		peered = _peered;
		val = data_wrapper_constructor.construct(init_val,peered);
	}
	
	@Override
	public void update_event_priority(String uuid, String new_priority) {
	}

	@Override
	public T get_val(LockedActiveEvent active_event) {
		return val.val;
	}

	/**
	 * Called as an active event runs code.
	 * @param active_event
	 * @param new_val
	 */
	@Override
	public void set_val(LockedActiveEvent active_event, T new_val) {
		// TODO Auto-generated method stub
		val.write(new_val);
	}

	@Override
	public boolean return_internal_val_from_container() {
		// TODO Auto-generated method stub
		return false;
	}

	/**
	 *         @returns {bool} --- True if the object has been written to
        since we sent the last message.  False otherwise.  (Including
        if event has been preempted.)
        

	 * @param active_event
	 * @return
	 */
	@Override
	public boolean get_and_reset_has_been_written_since_last_msg(
			LockedActiveEvent active_event) 
	{
        // check if active event even has ability to write to variable

		boolean has_been_written = val.get_and_reset_has_been_written_since_last_msg();
		return has_been_written;
	}

	@Override
	public void complete_commit(LockedActiveEvent active_event) {
		// nothing to do when completing commit: do nothing
	}

	@Override
	public boolean is_peered() {
		return peered;
	}

	@Override
	public void backout(LockedActiveEvent active_event) {
		/*
		 *         Do not actually need to remove changes to this variable: no
        other transaction will ever see the changes we made + this
        transaction will just create a new single threaded variable.

		 */
		return;
	}

	@Override
	public T de_waldoify(LockedActiveEvent active_event) {
        return val.de_waldoify(active_event);
	}

	@Override
	public abstract boolean serializable_var_tuple_for_network(VarStoreDeltas.Builder parent_delta,
			String var_name, LockedActiveEvent active_event, boolean force);

	@Override
	public abstract boolean serializable_var_tuple_for_network(
			waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas.SingleListDelta.Builder parent_delta,
			String var_name, LockedActiveEvent active_event, boolean force);

	@Override
	public abstract boolean serializable_var_tuple_for_network(
			waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas.SingleMapDelta.Builder parent_delta,
			String var_name, LockedActiveEvent active_event, boolean force);

	@Override
	public abstract boolean serializable_var_tuple_for_network(
			waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas.ContainerAction.ContainerAddedKey.Builder parent_delta,
			String var_name, LockedActiveEvent active_event, boolean force);

	@Override
	public abstract boolean serializable_var_tuple_for_network(
			waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas.SubElementUpdateActions.Builder parent_delta,
			String var_name, LockedActiveEvent active_event, boolean force);

	@Override
	public abstract boolean serializable_var_tuple_for_network(
			waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas.ContainerAction.ContainerWriteKey.Builder parent_delta,
			String var_name, LockedActiveEvent active_event, boolean force);

}
