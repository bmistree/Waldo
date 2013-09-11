package waldo;

import java.util.ArrayList;

import WaldoCallResults.EndpointCompleteCallResult;

public class ExecutingEvent 
{

	private String to_exec_internal_name;
	private LockedActiveEvent active_event;
	private ExecutingEventContext ctx;
	private java.util.concurrent.ArrayBlockingQueue<Object> result_queue;
	private Object[] to_exec_args;
	
	/**
    @param {Closure} to_exec_internal_name --- The internal
    name of the method to execute on this endpoint. 
    

    @param {_ActiveEvent object} active_event --- The active event
    object that to_exec should use for accessing endpoint data.

    @param {_ExecutingEventContext} ctx ---

    @param {result_queue or None} --- This value should be
    non-None for endpoint-call initiated events.  For endpoint
    call events, we wait for the endpoint to check if any of the
    peered data that it modifies also need to be modified on the
    endpoint's partner (and wait for partner to respond).  (@see
    discussion in waldoActiveEvent.wait_if_modified_peered.)  When
    finished execution, put wrapped result in result_queue.  This
    way the endpoint call that is waiting on the result can
    receive it.  Can be None only for events that were initiated
    by messages (in which the modified peered data would already
    have been updated).
    
    @param {*args} to_exec_args ---- Any additional arguments that
    get passed to the closure to be executed.
	*/
	public ExecutingEvent(String _to_exec_internal_name,LockedActiveEvent _active_event,
			ExecutingEventContext _ctx,java.util.concurrent.ArrayBlockingQueue<Object> _result_queue,
			Object..._to_exec_args)
	{
		to_exec_internal_name = _to_exec_internal_name;
		active_event = _active_event;
		ctx = _ctx;
		result_queue = _result_queue;
		to_exec_args = _to_exec_args;
	}
	
	
	/**
	 * @see arguments to constructor.
	 */
	public static void static_run(
			String to_exec_internal_name,LockedActiveEvent active_event,
			ExecutingEventContext ctx,java.util.concurrent.ArrayBlockingQueue<Object> result_queue,
			Object...to_exec_args)
	{
        Object result = active_event.event_parent.local_endpoint._dispatch_method(to_exec_internal_name,active_event,ctx,to_exec_args);
        
        if (result_queue == null)
        	return;
        
		//# check if the active event has touched any peered data.  if
		//# have, then send an update message to partner and wait for
		//# ack of message before returning.
        boolean completed = active_event.wait_if_modified_peered();
        
        if (! completed)
        {
            result_queue.add(
            		new WaldoCallResults.BackoutBeforeEndpointCallResult());
        }
        else
        {
        	result_queue.add(new EndpointCompleteCallResult(result));
        }		
	}
			
			
	public void run()
	{
		static_run(to_exec_internal_name,active_event,ctx,result_queue,to_exec_args);
	}
		
}
