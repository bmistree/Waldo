package WaldoExceptions;

public class WaldoHandleableException extends Exception {

	public String trace;
	
	public WaldoHandleableException(String _trace)
	{
		trace = _trace;
	}
}
