package library_tests;

import WaldoExceptions.ApplicationException;
import WaldoExceptions.BackoutException;
import WaldoExceptions.NetworkException;
import WaldoExceptions.StoppedException;
import waldo.LockedActiveEvent;
import waldo.LockedObject;
import waldo.LockedVariables;
import waldo.VariableStore;

public class EndpointCallTest implements TestInterface
{
	/**
	 * @param args
	 */
	public static void main(String[] args) 
	{
		if (run_static_test())
			System.out.println("\nSucceeded\n");
		else
			System.out.println("\nFailed\n");
				
	}
	
	public static boolean run_static_test()
	{
		return (new EndpointCallTest()).run_test();
	}

	private waldo.Endpoint create_single_endpoint()
	{
		String host_uuid = "host_uuid";
		String multi_num = "num_var";
			
		double initial_value = 30;
		VariableStore glob_var_store = new VariableStore(host_uuid);
		LockedVariables.LockedNumberVariable num_var = new LockedVariables.LockedNumberVariable(host_uuid, false, initial_value);
		glob_var_store.add_var(multi_num, num_var);
		test_util.SingleSidedEndpoint endpt = new test_util.SingleSidedEndpoint (host_uuid,glob_var_store);
		return endpt;
	}
	
	@Override
	public boolean run_test() 
	{
		// each endpoint has a number variable on it.
		waldo.Endpoint endpta = create_single_endpoint();
		waldo.Endpoint endptb = create_single_endpoint();
		
		waldo.ExecutingEventContext ctx = test_util.create_context(endpta);
		LockedActiveEvent active_event = null;
		try {
			active_event = endpta._act_event_map.create_root_event();
		} catch (StoppedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		
		Object result = null;
		try {
			LockedObject num_var =ctx.global_store.get_var_if_exists("num_var");
			Object[] _tmp_args0 = new Object[1];
			_tmp_args0[0] = num_var.get_val(active_event);
		
			result = ctx.hide_endpoint_call(active_event, ctx, endptb, "test_endpoint", _tmp_args0);
			
			
			Double val = (Double)ctx.get_val_if_waldo(result, active_event);
			
			if (val != 31)
				return false;
			
			active_event.begin_first_phase_commit();
			
			((waldo.RootEventParent)active_event.event_parent).event_complete_queue.take();
			
		} catch (NetworkException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (ApplicationException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (BackoutException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		
		
		
		return true;
	}
}