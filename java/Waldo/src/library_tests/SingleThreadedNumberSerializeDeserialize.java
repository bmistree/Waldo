package library_tests;

import waldo.LockedVariables;
import waldo.LockedVariables.SingleThreadedLockedNumberVariable;
import waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas;

public class SingleThreadedNumberSerializeDeserialize 
{
	/**
	 * Tests that can change a single threaded number, serialize it 
	 * to the other side, see the changes in that number and send it back.
	 */
	

	/**
	 * @param args
	 */
	public static void main(String[] args) 
	{
		if (run_test())
			System.out.println("\nSucceeded\n");
		else
			System.out.println("\nFailed\n");
				
	}
	
	
	public static boolean run_test()
	{
		SingleThreadedLockedNumberVariable num_var_side_a = 
				new LockedVariables.SingleThreadedLockedNumberVariable("dummy_host",true,303);
		SingleThreadedLockedNumberVariable num_var_side_b = 
				new LockedVariables.SingleThreadedLockedNumberVariable("dummy_host",true,null);
		
		//Try to serialize the number on one side and incorporate the changes on the other
		VarStoreDeltas.Builder parent_delta_builder = VarStoreDeltas.newBuilder();
		num_var_side_a.serializable_var_tuple_for_network(parent_delta_builder, "Some name", null, true);
		parent_delta_builder.setParentType(VarStoreDeltas.ParentType.VAR_STORE_DELTA);
		VarStoreDeltas parent_delta = parent_delta_builder.build();
		
		
		return true;
	}
	

}


