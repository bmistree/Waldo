package library_tests;

import java.util.concurrent.ArrayBlockingQueue;

import WaldoCallResults.RootCallResultObject;
import WaldoExceptions.BackoutException;
import WaldoExceptions.StoppedException;
import waldo.LockedActiveEvent;
import waldo.LockedVariables;
import waldo.VariableStore;


/**
 * Creates two writer events.  The one with the lower priority acquires a write lock
 * on a variable.  Then the one with the lower priority attempts to acquire a 
 * write lock on the same variable.  Test to ensure that the higher priority 
 * event can preempt the lower.
 *    
 */
public class MultiThreadedPreemption implements TestInterface{

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		if (new MultiThreadedPreemption().run_test())
			System.out.println("\n\nSuccess\n\n");
		else
			System.out.println("\n\nFailure\n\n");

	}
	
	
	@Override
	public boolean run_test() 
	{
		String host_uuid = "host_uuid";
		String multi_num = "multi_num";
			
		
		double dummy_val = 3;
		double initial_value = 30;
		double new_val = 31;
		VariableStore glob_var_store = new VariableStore(host_uuid);
		final LockedVariables.LockedNumberVariable num_var = new LockedVariables.LockedNumberVariable(host_uuid, false, initial_value);
		glob_var_store.add_var(multi_num, num_var);
		final test_util.SingleSidedEndpoint endpt = new test_util.SingleSidedEndpoint (host_uuid,glob_var_store);
		
		try
		{
			LockedActiveEvent write_event_high = endpt._act_event_map.create_root_event();
			LockedActiveEvent write_event_low =  endpt._act_event_map.create_root_event();
			
			num_var.set_val(write_event_low, dummy_val);
			num_var.set_val(write_event_high, new_val);

			write_event_high.begin_first_phase_commit();
			
			
			write_event_low.begin_first_phase_commit();
			
			
			LockedActiveEvent read_event = endpt._act_event_map.create_root_event();
			if (num_var.get_val(read_event).doubleValue() != new_val)
			{
				System.out.println("Got incorrect val");
				return false;
			}
			
			RootCallResultObject call_result = ((waldo.RootEventParent)write_event_low.event_parent).event_complete_queue.poll();
			boolean preempted = false;
			if (WaldoCallResults.RootCallResultObject.class.isInstance(call_result))
				preempted = true;
			
			if (! preempted)
			{
				System.out.println("Failure: did not preempt");
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
