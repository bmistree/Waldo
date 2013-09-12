package library_tests;

import WaldoConnObj.ConnectionObj;
import WaldoConnObj.SingleSideConnection;
import WaldoExceptions.BackoutException;
import waldo.Endpoint;
import waldo.EndpointConstructorObj;
import waldo.LockedVariables.SingleThreadedLockedNumberVariable;
import waldo.VariableStore;
import waldo.WaldoGlobals;

public class test_util 
{

	public static class SingleSidedEndpoint extends waldo.Endpoint
	{
		public SingleSidedEndpoint (String host_uuid,VariableStore glob_var_store)
		{
			super (new WaldoGlobals(),host_uuid,
					new SingleSideConnection(),
					glob_var_store);
			
		}
	}
	
	
	public static class SameHostEndpointConstructor implements EndpointConstructorObj
	{

		@Override
		public Endpoint construct(WaldoGlobals globals, String host_uuid,
				ConnectionObj conn_obj) 
		{
			Endpoint to_return = new SameHostEndpoint(host_uuid,new VariableStore(host_uuid), conn_obj); 
			to_return._this_side_ready();
			return to_return;
		}
	}
	
	
	public static class SameHostEndpoint extends waldo.Endpoint
	{
		public SameHostEndpoint (String host_uuid,VariableStore glob_var_store,WaldoConnObj.ConnectionObj conn_obj)
		{
			super (new WaldoGlobals(),host_uuid,
					conn_obj,
					glob_var_store);
			
		}
		
		public void _partner_endpoint_msg_func_call_prefix__waldo__test_partner(
				waldo.LockedActiveEvent active_event, waldo.ExecutingEventContext context, Object...args)
		{
			SingleThreadedLockedNumberVariable num_var = 
					(SingleThreadedLockedNumberVariable) context.sequence_local_store.get_var_if_exists("num_var");
			
			try {
				num_var.set_val(active_event, ( ((Number)context.get_val_if_waldo(num_var, active_event)).doubleValue() + 1));
			} catch (BackoutException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
			context.hide_sequence_completed_call(this, active_event);
			
		}
	}
	
	public static waldo.ExecutingEventContext create_context (waldo.Endpoint endpoint)
	{
		waldo.VariableStore seq_local_store = new VariableStore(endpoint._host_uuid);
		return new waldo.ExecutingEventContext(
	        endpoint._global_var_store,
	        seq_local_store);
	}

	
}

