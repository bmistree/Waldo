package library_tests;

import WaldoExceptions.BackoutException;
import WaldoExceptions.StoppedException;
import waldo.LockedActiveEvent;
import waldo.LockedVariables;
import waldo.VariableStore;


/**
 * Creates two events.  Each reads from num_var before committing.   
 * 
 */
public class MultithreadedNoConflict implements TestInterface{

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		if (new MultithreadedNoConflict().run_test())
			System.out.println("\n\nSuccess\n\n");
		else
			System.out.println("\n\nFailure\n\n");

	}

	@Override
	public boolean run_test() 
	{
		String host_uuid = "host_uuid";
		String multi_num = "multi_num";
			
		double initial_value = 30;
		VariableStore glob_var_store = new VariableStore(host_uuid);
		LockedVariables.LockedNumberVariable num_var = new LockedVariables.LockedNumberVariable(host_uuid, false, initial_value);
		glob_var_store.add_var(multi_num, num_var);
		test_util.SingleSidedEndpoint endpt = new test_util.SingleSidedEndpoint (host_uuid,glob_var_store);
		
		try
		{
			LockedActiveEvent read_event_one = endpt._act_event_map.create_root_event();
			double read_value = num_var.get_val(read_event_one).doubleValue();
			
			if (read_value != initial_value)
			{
				System.out.println("Read incorrect value from num_var on event 1.");
				return false;
			}
			
			LockedActiveEvent read_event_two = endpt._act_event_map.create_root_event();
			read_value = num_var.get_val(read_event_two).doubleValue();
			if (read_value != initial_value)
			{
				System.out.println("Read incorrect value from num_var on event 2.");
				return false;
			}
			
			
			read_event_one.begin_first_phase_commit();
			read_event_two.begin_first_phase_commit();

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
