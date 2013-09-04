package WaldoCallResults;
import java.util.ArrayList;

public class EndpointCallResult 
{
	public ArrayList<Object> result_array;
	
	/**
	 *  When an active event issues an endpoint call, it blocks on reading a
		threadsafe queue.  If the invalidation event has been backed out
		before the endpoint call completes, we put a
		_BackoutBeforeEndpointCallResult into the queue so that the event
		knows not to perform any additional work.  Otherwise, put an
		_EndpointCallResult in, which contains the returned values.
	 * @param _result_array
	 */
	public EndpointCallResult (ArrayList<Object>_result_array)
	{
		result_array = _result_array;
	}
}
