package waldo;

public class Stoppable {
	private java.util.concurrent.atomic.AtomicBoolean _is_stopped = new java.util.concurrent.atomic.AtomicBoolean(false);
	
	public void stop()
	{
		_is_stopped.set(true);
	}
	public boolean is_stopped ()
	{
		return _is_stopped.get();
	}
}
