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
				
		VariableStore glob_var_store = new VariableStore(host_uuid);
		LockedVariables.LockedNumberVariable num_var = new LockedVariables.LockedNumberVariable(host_uuid, false, 30);
		glob_var_store.add_var(multi_num, num_var);
		
		test_util.SingleSidedEndpoint endpt = new test_util.SingleSidedEndpoint (host_uuid,glob_var_store);
		
		LockedActiveEvent active_event = null;
		try {
			active_event = endpt._act_event_map.create_root_event();
		} catch (StoppedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		
		Double read_value = null;
		try
		{
			Number tmp = num_var.get_val(active_event);
			read_value = tmp.doubleValue();
		} catch (Exception e){}
		
		if (read_value != 30)
		{
			System.out.println("Read incorrect value from num_var");
			return false;
		}
		
		
		active_event.begin_first_phase_commit();
		
		
		return true;
	}

}
