package library_tests;

import waldo.LockedVariables;
import waldo.LockedVariables.SingleThreadedLockedNumberVariable;
import waldo.VariableStore;
import waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas;
import waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas.Builder;

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
		String host_uuid_a = "a";
		String host_uuid_b = "b";
		VariableStore var_store_a = new VariableStore(host_uuid_a);
		VariableStore var_store_b = new VariableStore(host_uuid_b);
		
		// create number variables on either side and put them in their respective 
		// variable stores.
		String common_var_name = "common_name";
		double side_a_init_val = 303;
		SingleThreadedLockedNumberVariable num_var_side_a = 
				new LockedVariables.SingleThreadedLockedNumberVariable(host_uuid_a,true,side_a_init_val);
		SingleThreadedLockedNumberVariable num_var_side_b = 
				new LockedVariables.SingleThreadedLockedNumberVariable(host_uuid_b,true,null);
		
		var_store_a.add_var(common_var_name, num_var_side_a);
		var_store_b.add_var(common_var_name, num_var_side_b);
		
		// generate the deltas on one side and send them to the other
		VarStoreDeltas.Builder deltas = var_store_a.generate_deltas(null, true);
		
		var_store_b.incorporate_deltas(null, deltas.build());
		
		// check that value of b now equals that of a
		SingleThreadedLockedNumberVariable updated_side_b = (SingleThreadedLockedNumberVariable)var_store_b.get_var_if_exists(common_var_name);
		
		if (updated_side_b.get_val(null).doubleValue() != side_a_init_val )
		{
			System.out.println("Incorrect value on side b after serialization.");
			return false;
		}
		
		
		
		/*
		//Try to serialize the number on one side and incorporate the changes on the other
		VarStoreDeltas.Builder parent_delta_builder = VarStoreDeltas.newBuilder();
		num_var_side_a.serializable_var_tuple_for_network(parent_delta_builder, "Some name", null, true);
		parent_delta_builder.setParentType(VarStoreDeltas.ParentType.VAR_STORE_DELTA);
		VarStoreDeltas parent_delta = parent_delta_builder.build();
		*/
		
		return true;
	}
	

}


