package library_tests;

import WaldoConnObj.SingleSideConnection;
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
}
