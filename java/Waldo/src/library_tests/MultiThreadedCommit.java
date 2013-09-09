package library_tests;


import WaldoExceptions.StoppedException;
import waldo.LockedActiveEvent;
import waldo.LockedVariables;
import waldo.VariableStore;


/**
 * Creates a multithreaded variable, reads that variable, writes that variable, reads that variable
 * Creates two events.  Each reads from num_var before committing.   
 * 
 */
public class MultiThreadedCommit implements TestInterface{

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		if (new MultiThreadedCommit().run_test())
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
		double new_value = 40;
		
		VariableStore glob_var_store = new VariableStore(host_uuid);
		LockedVariables.LockedNumberVariable num_var = new LockedVariables.LockedNumberVariable(host_uuid, false, initial_value);
		glob_var_store.add_var(multi_num, num_var);
		
		test_util.SingleSidedEndpoint endpt = new test_util.SingleSidedEndpoint (host_uuid,glob_var_store);
		
		
		try
		{
			// Perform first read on variable to ensure that default value is correct
			LockedActiveEvent first_read_event = endpt._act_event_map.create_root_event();
			Double read_value = num_var.get_val(first_read_event).doubleValue();
			if (read_value != initial_value)
			{
				System.out.println("Read incorrect value from num_var");
				return false;
			}
			first_read_event.begin_first_phase_commit();
			
			
			// create a new event and write to variable
			LockedActiveEvent write_event = endpt._act_event_map.create_root_event();
			num_var.set_val(write_event, new_value);
			
			read_value = num_var.get_val(write_event).doubleValue();
			if (read_value != new_value)
			{
				System.out.println("Read incorrect value from num_var during write");
				return false;
			}
			write_event.begin_first_phase_commit();
			
			
			// perform read with separate event to ensure that new value stays after commit
			LockedActiveEvent second_read_event = endpt._act_event_map.create_root_event();
			read_value = num_var.get_val(second_read_event).doubleValue();
			if (read_value != new_value)
			{
				System.out.println("Read incorrect value from num_var after write");
				return false;
			}
			
		
		} catch(WaldoExceptions.BackoutException e)
		{
			e.printStackTrace();
			return false;
		}
		catch (StoppedException e)
		{
			e.printStackTrace();
			return false;
		}
		
		
		return true;
	}

}
