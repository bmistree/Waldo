package waldo;

public class WaldoGlobals {
	public Clock clock;
	public AllEndpoints all_endpoints;
	public ThreadPool thread_pool;
	
	public WaldoGlobals()
	{
		all_endpoints = new AllEndpoints();
		clock = new Clock(all_endpoints);
		thread_pool = new ThreadPool(Util.DEFAULT_NUM_THREADS);		
	}
	
}
