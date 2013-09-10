package waldo;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import WaldoServiceActions.ServiceAction;

public class ThreadPool 
{
	private ExecutorService executor = null;
	
	public ThreadPool(int num_threads)
	{
		executor = Executors.newFixedThreadPool(num_threads);
	}
	
	public void add_service_action(ServiceAction service_action)
	{
		executor.execute(service_action);
	}
		
}

