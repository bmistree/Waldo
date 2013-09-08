package waldo;

import java.util.ArrayList;

public class EventSubscribedTo 
{
	private Endpoint endpoint_object = null;
	public ArrayList<
	    java.util.concurrent.ArrayBlockingQueue<EndpointResultObject>> result_queues = 
	    
	    new ArrayList<java.util.concurrent.ArrayBlockingQueue<EndpointResultObject>>(); 
	
	
	
    /**
    @param {_Endpoint object} --- The endpoint object that we are
    subscribed to.

    @param {Queue.Queue} result_queue --- @see add_result_queue
	*/
	public EventSubscribedTo(Endpoint _endpoint_object, java.util.concurrent.ArrayBlockingQueue<EndpointResultObject> queue)
	{
		endpoint_object = _endpoint_object;
		add_result_queue(queue);
	}


	/**
	@param {Queue.Queue} result_queue --- Whenever we make an
	endpoint call on another endpoint object, we listen for the
	call's return value on result_queue.  When we backout an
	event, we put a backout sentinel value into the result queue
	so that any code that was waiting on the result of the
	endpoint call knows to stop executing.  We maintain all
	result_queues in SubscribedToElement so that we can write this
	sentinel into them if we backout.  (Note: the sentinel is
	waldoCallResults._BackoutBeforeEndpointCallResult)
	*/
	public void add_result_queue(java.util.concurrent.ArrayBlockingQueue<EndpointResultObject>result_queue)
	{
		result_queues.add(result_queue);
	}

	
}
