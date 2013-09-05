package waldo;

import java.util.ArrayList;
import java.util.HashMap;

import waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas.SingleInternalListDelta;
import waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas.SingleInternalMapDelta;

public interface ContainerInterface <K,V,D>{
	
	public V get_val_on_key(LockedActiveEvent active_event, K key);
	/**
	 * If we are trying to get a container variable or external variable, use this method instead.  It  
	 * lets you keep using the locked object interface to access internal data.
	 * @param active_event
	 * @param key
	 * @return
	 */
	public LockedObject<V,D> get_locked_obj_val_on_key(LockedActiveEvent active_event,K key);
	public void set_val_on_key(LockedActiveEvent active_event, K key, V to_write, boolean copy_if_peered);
	public void set_val_on_key(LockedActiveEvent active_event, K key, V to_write);
	public void del_key_called(LockedActiveEvent active_event,K key_to_delete);
	public int get_len(LockedActiveEvent active_event);
	public ArrayList<K> get_keys(LockedActiveEvent active_event);
	public boolean contains_key_called(LockedActiveEvent active_event, K contains_key);
	public boolean contains_val_called(LockedActiveEvent active_event,V contains_val);
	
	/**
	 * @see waldoLockedObj.waldoLockedObj
	 * @param active_event
	 * @return
	 */
	public DataWrapper<HashMap<K,V>, HashMap<K,D>> get_dirty_wrapped_val(LockedActiveEvent active_event);

	/**
	 *@param {SingleListDelta or SingleMapDelta} delta_to_incorporate

		@param {SingleInternalListDelta or SingleInternalMapDelta}
		delta_to_incorporate
		
		When a peered or sequence peered container (ie, map, list, or
		struct) is modified by one endpoint, those changes must be
		reflected on the other endpoint.  This method takes the
		changes that one endpoint has made on a container, represented
		by delta_to_incorporate, and applies them (if we can).
	 */
	public void incorporate_deltas(SingleInternalListDelta delta_to_incorporate, LockedActiveEvent active_event);
	public void incorporate_deltas(SingleInternalMapDelta delta_to_incorporate, LockedActiveEvent active_event);
	    		
}
