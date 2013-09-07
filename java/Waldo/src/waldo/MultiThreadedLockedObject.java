package waldo;

import java.util.HashMap;

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
	private java.util.concurrent.locks.ReentrantLock _mutex = new java.util.concurrent.locks.ReentrantLock();
	public DataWrapper<T,D> dirty_val = null;
		
	//# If write_lock_holder is not None, then the only element in
	//# read_lock_holders is the write lock holder.
	//# read_lock_holders maps from uuids to EventCachedPriorityObj.
    private HashMap<String, EventCachedPriorityObj>read_lock_holders = new HashMap<String,EventCachedPriorityObj>();
    
	//# write_lock_holder is EventCachedPriorityObj
    private EventCachedPriorityObj write_lock_holder = null; 

    
	//# A dict of event uuids to WaitingEventTypes
    private HashMap<String,WaitingElement<T,D>>waiting_events =
    		new HashMap<String, WaitingElement<T,D>>();

	//# In try_next, can cause events to backout.  If we do cause
	//# other events to backout, then backout calls try_next.  This
	//# (in some cases) can invalidate state that we're already
	//# dealing with in the parent try_next.  Use this flag to keep
	//# track of whether already in try next.  If are, then return
	//# out immediately from future try_next calls.
    private boolean in_try_next = false;
    
    
    /**
     * Used by 
     */
    private class EventCachedPriorityObj
    {
    	String cached_priority = "";
    	LockedActiveEvent event = null;
    	public EventCachedPriorityObj (LockedActiveEvent active_event,String _cached_priority)
    	{
    		event = active_event;
    		cached_priority = _cached_priority;
    	}
    }
	
	
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
		
		_lock();
		//# Each event has a priority associated with it.  This priority
		//# can change when an event gets promoted to be boosted.  To
		//# avoid the read/write conflicts this might cause, at the
		//# beginning of acquring read lock, get priority and use that
		//# for majority of time trying to acquire read lock.  If cached
		//# priority ends up in WaitingElement, another thread can later
		//# update it.
        String cached_priority = active_event.get_priority();
        
        
		//# must be careful to add obj to active_event's touched_objs.
		//# That way, if active_event needs to backout, we're guaranteed
		//# that the state we've allocated for accounting the
		//# active_event is cleaned up here.
        if (! insert_in_touched_objs(active_event))
        {
            _unlock();
            throw new WaldoExceptions.BackoutException();
        }

		//# check 0 above
        if ((write_lock_holder != null) &&
        	(active_event.uuid == write_lock_holder.event.uuid))
        {
        	DataWrapper<T,D> to_return = dirty_val;
            _unlock();
            return to_return;
        }

		//# also check 1 above
        if (read_lock_holders.containsKey(active_event.uuid))
        {
			//# already allowed to read the variable
        	DataWrapper<T,D> to_return = val;
            _unlock();
            return to_return;
        }

		//# must be careful to add obj to active_event's touched_objs.
		//# That way, if active_event needs to backout, we're guaranteed
		//# that the state we've allocated for accounting the
		//# active_event is cleaned up here.
        if (! insert_in_touched_objs(active_event))
        {
        	_unlock();
        	throw new WaldoExceptions.BackoutException();
        }

		//# Check 2 from above
        
		//# check 2a
        if (write_lock_holder == null)
        {
        	DataWrapper<T,D> to_return = val;
            read_lock_holders.put(
            	active_event.uuid,
            	new EventCachedPriorityObj(active_event,cached_priority));
            _unlock();
            return to_return;
        }

		//# check 2b
        if (EventPriority.gte_priority(cached_priority, write_lock_holder.cached_priority))
        {
			//# backout write lock if can
        	if (write_lock_holder.event.can_backout_and_hold_lock())
        	{
        		//# actually back out the event
        		obj_request_backout_and_release_lock(write_lock_holder.event);

        		//# add active event as read lock holder and return
                dirty_val = null;
                write_lock_holder = null;
                read_lock_holders = 
                		new HashMap<String,EventCachedPriorityObj>();
                read_lock_holders.put(
                		active_event.uuid, new EventCachedPriorityObj(active_event,cached_priority));
                		
                DataWrapper<T,D> to_return = val;
                _unlock();
                return to_return;
        	}
        }
                		

		//# Condition 2c + 3
		//
		//# create a waiting read element
        WaitingElement<T,D> waiting_element =
        		new WaitingElement(active_event,cached_priority,true,data_wrapper_constructor,peered);

        waiting_events.put(active_event.uuid, waiting_element);
        _unlock();

        return waiting_element.queue.take();
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
	private DataWrapper<T,D> acquire_write_lock(LockedActiveEvent active_event)
	{
        _lock();
		//# Each event has a priority associated with it.  This priority
		//# can change when an event gets promoted to be boosted.  To
		//# avoid the read/write conflicts this might cause, at the
		//# beginning of acquring write lock, get priority and use that
		//# for majority of time trying to acquire read lock.  If cached
		//# priority ends up in WaitingElement, another thread can later
		//# update it.
        String cached_priority = active_event.get_priority();
        
		//# must be careful to add obj to active_event's touched_objs.
		//# That way, if active_event needs to backout, we're guaranteed
		//# that the state we've allocated for accounting the
		//# active_event is cleaned up here.
        if (! insert_in_touched_objs(active_event))
        {
        	_unlock();
        	throw new WaldoExceptions.BackoutException();
        }


		//# case 0 above
        if ((write_lock_holder != null) &&
        		(active_event.uuid == write_lock_holder.event.uuid))
        {
        	DataWrapper<T,D> to_return = dirty_val;
        	_unlock();
        	return to_return;
        }	
        
		//# case 1 above
        if ((write_lock_holder != null) && 
        		read_lock_holders.isEmpty())
        {
        	Util.logger_warn("Grabbing internal value of val.  Different from python.");
        	dirty_val = data_wrapper_constructor.construct(val.val, peered);
        	write_lock_holder = new EventCachedPriorityObj(active_event,cached_priority);
        	read_lock_holders.put(
        			active_event.uuid,
        			new EventCachedPriorityObj(active_event,cached_priority));
        	DataWrapper<T,D> to_return = dirty_val;
        	_unlock();
        	return to_return;
        }

        
        if (is_gte_than_lock_holding_events(cached_priority))
        {
			//# Stage 2 from above
        	if (test_and_backout_all(active_event.uuid))
        	{
				//# Stage 3 from above
				//# actually update the read/write lock holders
        		read_lock_holders.put(
        				active_event.uuid, 
        				new EventCachedPriorityObj(active_event,cached_priority));

        		write_lock_holder = new EventCachedPriorityObj(active_event,cached_priority);
        		Util.logger_warn("Grabbing internal value of val.  Different from python.");
        		dirty_val = data_wrapper_constructor.construct(val.val,peered);
        		DataWrapper<T,D> to_return = dirty_val;
        		_unlock();
                return to_return;
        	}
        }

        
        //# case 3: add to wait queue and wait
        WaitingElement <T,D> write_waiting_event = new WaitingElement<T,D>(
        		active_event,cached_priority,false,data_wrapper_constructor,
        		peered);
        waiting_events.put(active_event.uuid, write_waiting_event);        
        _unlock();
        return write_waiting_event.queue.take();
	}
	
	

	
}