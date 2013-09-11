package WaldoCallResults;

public class ApplicationExceptionEndpointCallResult extends
		EndpointCallResultObject {
	
	private String trace;
	
	public ApplicationExceptionEndpointCallResult(String _trace)
	{
		trace = _trace;
	}

	public String get_trace() {
		// TODO Auto-generated method stub
		return trace;
	}

}
