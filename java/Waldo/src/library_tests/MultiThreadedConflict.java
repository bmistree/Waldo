package library_tests;

import java.util.concurrent.ArrayBlockingQueue;

import WaldoExceptions.BackoutException;
import WaldoExceptions.StoppedException;
import waldo.LockedActiveEvent;
import waldo.LockedVariables;
import waldo.VariableStore;


/**
 * Creates two events.  One is a writer.  One is a reader.  The writer write 
 * locks the variable and sleeps briefly.  While the writer is asleep, the reader
 * tries to read the variable and put the result into a shared threadsafe queue.
 * 
 * After some time, the writer wakes up and puts a sentinel value in the threadsafe 
 * queue and commits itself.  If the contents of the threadsafe queue have the
 * readers value before the sentinel value, then this means that the read event
 * did not properly block on acquiring a read lock on the variable.  If the 
 * sentinel appears before the read value, then it did.
 *    
 */
public class MultiThreadedConflict implements TestInterface{

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		if (new MultiThreadedConflict().run_test())
			System.out.println("\n\nSuccess\n\n");
		else
			System.out.println("\n\nFailure\n\n");

	}
	
	
	

	@Override
	public boolean run_test() 
	{
		String host_uuid = "host_uuid";
		String multi_num = "multi_num";
			
		// both the reader and the writer put values
		final ArrayBlockingQueue<Double> between_queue = new ArrayBlockingQueue<Double>(3);
		
		double write_thread_sentinel = -39;
		double initial_value = 30;
		double new_val = 31;
		VariableStore glob_var_store = new VariableStore(host_uuid);
		final LockedVariables.LockedNumberVariable num_var = new LockedVariables.LockedNumberVariable(host_uuid, false, initial_value);
		glob_var_store.add_var(multi_num, num_var);
		final test_util.SingleSidedEndpoint endpt = new test_util.SingleSidedEndpoint (host_uuid,glob_var_store);
		
		try
		{
			LockedActiveEvent write_event = endpt._act_event_map.create_root_event();
			num_var.set_val(write_event, new_val);

			// create a thread that tries to read from variable and puts the 
			// result in between_queue.
			new Thread()
			{
				public void run()
				{
					try
					{
						LockedActiveEvent read_event;
						read_event = endpt._act_event_map.create_root_event();
						between_queue.add((Double) num_var.get_val(read_event));
						read_event.begin_first_phase_commit();
					} catch(BackoutException e){}
				  	  catch (StoppedException e) {}

				}
			}.start();
			
			
			// even if we sleep for a little time, the above thread should still
			// be blocked on 
			try {
			    Thread.sleep(1000);
			} catch(InterruptedException ex) {
			    Thread.currentThread().interrupt();
			}	
			
			between_queue.add(write_thread_sentinel);
			write_event.begin_first_phase_commit();
			
			
			
			// read the queue.  null should be first.
			Double element = between_queue.poll();
			if (element != write_thread_sentinel)
			{
				System.out.println("Out of order queue");
				return false;
			}
			
			element = between_queue.poll();
			if (element != new_val)
			{
				System.out.println("Incorrect val in queue");
				return false;
			}
			
			element = between_queue.poll();
			if (element != null)
			{
				System.out.println("Too many values in queue");
				return false;
			}
			
		}
		catch (StoppedException e)
		{
			e.printStackTrace();
			return false;
		}
		catch (BackoutException e)
		{
			e.printStackTrace();
			return false;
		}
		
		return true;
	}

}
