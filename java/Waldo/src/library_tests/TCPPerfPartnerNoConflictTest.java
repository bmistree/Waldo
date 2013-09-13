package library_tests;

import java.io.IOException;
import java.util.Random;
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
import waldo.Waldo;

public class TCPPerfPartnerNoConflictTest implements TestInterface
{

	public static void main(String[] args) {
		if (new TCPPerfPartnerNoConflictTest().run_test())
			System.out.println("\n\nSuccess\n\n");
		else
			System.out.println("\n\nFailure\n\n");

	}
	
	public boolean run_seq(Endpoint endpta, String host_uuid, double initial_value, String seq_local_num, double new_val)
	{
		waldo.ExecutingEventContext ctx = test_util.create_context(endpta);
		
		try {
			LockedActiveEvent multi_event;
			multi_event = endpta._act_event_map.create_root_event();
			
			// create sequence local variable
			LockedVariables.SingleThreadedLockedNumberVariable num_var = 
					new LockedVariables.SingleThreadedLockedNumberVariable(host_uuid, true, initial_value);
			ctx.sequence_local_store.add_var(seq_local_num, num_var);
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
		    
		    try {
				((waldo.RootEventParent)multi_event.event_parent).event_complete_queue.take();
			} catch (InterruptedException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		    
			
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
		
		String host = "127.0.0.1";
		
		//int port = 39399;
		Random randomer = new Random();
		int port = (java.lang.Math.abs((randomer.nextInt()) % 40000)) + 1200;
		
		//WaldoConnObj.SameHostConnection conn_obj = new WaldoConnObj.SameHostConnection();
		Waldo.tcp_accept(new test_util.SameHostEndpointConstructor(), host, port);
		
		Endpoint endpta = null;
		try {
			endpta = Waldo.tcp_connect(new test_util.SameHostEndpointConstructor(), host, port);
		} catch (IOException e) {
			e.printStackTrace();
		}
		
		System.out.println("\nFirst\n");
		int num_times = 30000;
		//int num_times = 100;
		for (int i =0; i < num_times; ++i)
			run_seq( endpta, host_uuid, initial_value, seq_local_num, new_val);

		System.out.println("\nSecond\n");
		
		long start_time = System.nanoTime();
		
		for (int i =0; i < num_times; ++i)
			run_seq( endpta, host_uuid, initial_value, seq_local_num, new_val);
		
		long finish_time = System.nanoTime();
		System.out.println((finish_time - start_time)/1e9);
		System.out.println(num_times);
		
		
		return true;
		
	}

	
}
