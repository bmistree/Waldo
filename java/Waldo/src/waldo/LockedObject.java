package waldo;

import waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas;
import waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas.ContainerAction;
import waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas.ContainerAction.ContainerAddedKey;
import waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas.ContainerAction.ContainerWriteKey;
import waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas.SingleListDelta;
import waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas.SingleMapDelta;
import waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas.SingleNumberDelta;
import waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas.SingleTextDelta;
import waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas.SingleTrueFalseDelta;
import waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas.SubElementUpdateActions;


public abstract class LockedObject<T> {

	private MultiThreadedConstructor multi_threaded_constructor = null;
	private SingleThreadedConstructor single_threaded_constructor = null;
	
	protected String host_uuid = null;
	
	public LockedObject<T> copy(LockedActiveEvent active_event, boolean peered, boolean multi_threaded)
	{
		if (multi_threaded)
			return multi_threaded_constructor.construct(host_uuid,peered,get_val(active_event));
		
		return single_threaded_constructor.construct(host_uuid,peered,get_val(active_event));
	}
	
	
	/**
	 * 
        Called when an event with uuid "uuid" is promoted to boosted
        with priority "priority"
     * @param uuid
	 * @param new_priority
	 */
	public abstract void update_event_priority(String uuid,String new_priority); 

	public abstract T get_val(LockedActiveEvent active_event);

    public abstract void set_val(LockedActiveEvent active_event, T new_val);

    /**
     *         @returns {bool} --- True if when call get_val_from_key on a
        container should call get_val on it.  False otherwise.
     */
    public abstract boolean return_internal_val_from_container();

    /**
     * @returns {bool} --- True if the object has been written to
        since we sent the last message.  False otherwise.  (Including
        if event has been preempted.)
        
     */
    public abstract boolean get_and_reset_has_been_written_since_last_msg(LockedActiveEvent active_event);
    
    
    public abstract void complete_commit(LockedActiveEvent active_event);

    public abstract boolean is_peered();

    public abstract void backout(LockedActiveEvent active_event);

    public abstract T de_waldoify(LockedActiveEvent active_event);


    /**
     *         The runtime automatically synchronizes data between both
        endpoints.  When one side has updated a peered variable, the
        other side needs to attempt to apply those changes before
        doing further work.  This method grabs the val and version
        object of the dirty element associated with invalid_listener.
        Using these data, plus var_name, it constructs a named tuple
        for serialization.  (@see
        util._generate_serialization_named_tuple)

        Note: if the val of this object is another Reference object,
        then we recursively keep generating named tuples and embed
        them in the one we return.

        Note: we only serialize peered data.  No other data gets sent
        over the network; therefore, it should not be serialized.

        @param {*Delta or VarStoreDeltas} parent_delta --- Append any
        message that we create here to this message.
        
        @param {String} var_name --- Both sides of the connection need
        to agree on a common name for the variable being serialized.
        This is to ensure that when the data are received by the other
        side we know which variable to put them into.  This value is
        only really necessary for the outermost wrapping of the named
        type tuple, but we pass it through anyways.

        @param {bool} force --- True if regardless of whether modified
        or not we should serialize.  False otherwise.  (We migth want
        to force for instance the first time we send sequence data.)
        
        @returns {bool} --- True if some subelement was modified,
        False otherwise.
     */
    public abstract boolean serializable_var_tuple_for_network(
        VarStoreDeltas.Builder parent_delta,String var_name,LockedActiveEvent active_event,boolean force);
    public abstract boolean serializable_var_tuple_for_network(
            SingleNumberDelta.Builder parent_delta,String var_name,LockedActiveEvent active_event,boolean force);
    public abstract boolean serializable_var_tuple_for_network(
            SingleTextDelta.Builder parent_delta,String var_name,LockedActiveEvent active_event,boolean force);
	public abstract boolean serializable_var_tuple_for_network(
            SingleTrueFalseDelta.Builder parent_delta,String var_name,LockedActiveEvent active_event,boolean force);
	public abstract boolean serializable_var_tuple_for_network(
            SingleListDelta.Builder parent_delta,String var_name,LockedActiveEvent active_event,boolean force);
	public abstract boolean serializable_var_tuple_for_network(
            SingleMapDelta.Builder parent_delta,String var_name,LockedActiveEvent active_event,boolean force);
	public abstract boolean serializable_var_tuple_for_network(
            ContainerAddedKey.Builder parent_delta,String var_name,LockedActiveEvent active_event,boolean force);
	public abstract boolean serializable_var_tuple_for_network(
			SubElementUpdateActions.Builder parent_delta,String var_name,LockedActiveEvent active_event,boolean force);
	public abstract boolean serializable_var_tuple_for_network(
			ContainerWriteKey.Builder parent_delta,String var_name,LockedActiveEvent active_event,boolean force);
	
	
}