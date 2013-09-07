package waldo;

/**
 * 
 * @author bmistree
 *
 * @param <T> --- The java type of the internal data
 * @param <D> --- The type that gets returned from dewaldoify.  Not entirely true
 * If this is an internal container, then contains what each value in map/list would dewaldoify to.
 */
public abstract class MultiThreadedLockedObject<T,D> extends LockedObject<T,D> 
{
	public String uuid = Util.generate_uuid();
	public String host_uuid = null;
	public boolean peered;
	private DataWrapperConstructor<T,D> data_wrapper_constructor;
	public DataWrapper<T,D> val = null;
	
	public DataWrapper<T,D> dirty_val = null;
	
	public MultiThreadedLockedObject(){}
	
	public void init(
			ValueTypeDataWrapperConstructor<T,D> vtdwc, String _host_uuid,boolean _peered, T init_val)
	{
		data_wrapper_constructor = vtdwc;
		host_uuid = _host_uuid;
		peered = _peered;
		val = data_wrapper_constructor.construct(init_val,peered);
	}
	
	private void _lock()
	{
		_mutex.lock();
	}
	private void _unlock()
	{
		_mutex.unlock();
	}
	
	
	/**
	 * 
        DOES NOT ASSUME ALREADY WITHIN LOCK

        @returns {DataWrapper object}

        Algorithms:

           0) If already holds a write lock on the variable, then
              return the dirty value associated with event.
           
           1) If already holds a read lock on variable, returns the value
              immediately.

           2) If does not hold a read lock on variable, then attempts
              to acquire one.  If worked, then return the variable.
              When attempting to acquire read lock:

                 a) Checks if there is any event holding a write lock.
                    If there is not, then adds itself to read lock
                    holder dict.
              
                 b) If there is another event holding a write lock,
                    then check if uuid of the read lock requester is
                    >= uuid of the write lock.  If it is, then try to
                    backout the holder of write lock.

                 c) If cannot backout or have a lesser uuid, then
                    create a waiting event and block while listening
                    to queue.  (same as #3)
              
           3) If did not work, then create a waiting event and a queue
              and block while listening on that queue.

        Blocks until has acquired.
	 */
	private DataWrapper<T,D> acquire_read_lock(LockedActiveEvent active_event)
	{
		// FIXME: finish
	}
	
	
	
	/**
	 * DOES NOT ASSUME ALREADY LOCK
	 * 
        0) If already holding a write lock, then return the dirty value

        1) If there are no read or write locks, then just copy the
           data value and set read and write lock holders for it.

        2) There are existing read and/or write lock holders.  Check
           if our uuid is larger than their uuids.
        
	 * @param active_event
	 * @return
	 */
	private DataWrapper<T,D> acquire_write_lock(LockedActiveVent active_event)
	{
		// FIXME: finish
	}
	
	

	
}