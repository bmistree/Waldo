package library_tests;

import java.util.concurrent.ArrayBlockingQueue;

import WaldoExceptions.ApplicationException;
import WaldoExceptions.BackoutException;
import WaldoExceptions.NetworkException;
import WaldoExceptions.StoppedException;

import library_tests.test_util.SameHostEndpoint;

import waldo.Endpoint;
import waldo.LockedActiveEvent;
import waldo.LockedVariables;
import waldo.VariableStore;

public class PerfPartnerNoConflictTest implements TestInterface
{

	public static void main(String[] args) {
		if (new PerfPartnerNoConflictTest().run_test())
			System.out.println("\n\nSuccess\n\n");
		else
			System.out.println("\n\nFailure\n\n");

	}
	
	public boolean run_seq(Endpoint endpta, Endpoint endptb, String host_uuid, double initial_value, String seq_local_num, double new_val)
	{
		waldo.ExecutingEventContext ctx = test_util.create_context(endpta);
		
		try {
			
			// create sequence local variable
			LockedVariables.SingleThreadedLockedNumberVariable num_var = 
					new LockedVariables.SingleThreadedLockedNumberVariable(host_uuid, true, initial_value);
			ctx.sequence_local_store.add_var(seq_local_num, num_var);
			
			LockedActiveEvent multi_event;
				multi_event = endpta._act_event_map.create_root_event();
			num_var.set_val(multi_event, new_val);
			
			
			// send message to other side
			//# send sequence message to the other side to perform write there.
			//# block until call completes
			
			ctx.hide_partner_call(
			        endpta,multi_event,"test_partner",true);
			
			
			// check that change from msg. to other side changed the var
			LockedVariables.SingleThreadedLockedNumberVariable nv = 
					(LockedVariables.SingleThreadedLockedNumberVariable)ctx.sequence_local_store.get_var_if_exists(seq_local_num);
			
			if ( ((Double) nv.get_val(multi_event)).doubleValue() != (new_val+1))
			{
				System.out.println("Received incorrect result from other side");
				return false;
			}
			
			
			//# actually try to commit write event
		    multi_event.begin_first_phase_commit();
			
		} catch (StoppedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
			return false;
		} catch (NetworkException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
			return false;
		} catch (ApplicationException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
			return false;
		} catch (BackoutException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
			return false;
		}
		return true;
		
	}
	
	
	

	@Override
	public boolean run_test() 
	{
		String host_uuid = "host_uuid";
		String seq_local_num = "num_var";
			
		// both the reader and the writer put values
		double initial_value = 30;
		double new_val = 31;
		VariableStore glob_var_store = new VariableStore(host_uuid);
		
		WaldoConnObj.SameHostConnection conn_obj = new WaldoConnObj.SameHostConnection();
		
		SameHostEndpoint endpta = new SameHostEndpoint (host_uuid,glob_var_store,conn_obj);
		SameHostEndpoint endptb = new SameHostEndpoint (host_uuid,glob_var_store,conn_obj);
		
		long start_time = System.nanoTime();
		
		for (int i =0; i < 10000; ++i)
			run_seq( endpta, endptb, host_uuid, initial_value, seq_local_num, new_val);
		
		long finish_time = System.nanoTime();
		System.out.println((finish_time - start_time)/1e9);
		
		return true;
		
	}

	
}
