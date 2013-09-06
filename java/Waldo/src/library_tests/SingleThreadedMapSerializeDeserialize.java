package library_tests;

import waldo.LockedVariables;
import waldo.LockedVariables.SingleThreadedLockedMapVariable;
import waldo.LockedVariables.SingleThreadedLockedNumberVariable;
import waldo.VariableStore;
import waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas;
import waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas.Builder;
import java.util.HashMap;


public class SingleThreadedMapSerializeDeserialize implements TestInterface
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
		if (run_static_test())
			System.out.println("\nSucceeded\n");
		else
			System.out.println("\nFailed\n");
				
	}
	
	public static boolean run_static_test()
	{
		return (new SingleThreadedMapSerializeDeserialize()).run_test();
	}
	
	public boolean run_test()
	{
		String host_uuid_a = "a";
		String host_uuid_b = "b";
		VariableStore var_store_a = new VariableStore(host_uuid_a);
		VariableStore var_store_b = new VariableStore(host_uuid_b);
		
		// create number variables on either side and put them in their respective 
		// variable stores.
		String common_var_name = "common_name";
		double side_a_init_val = 303;
		
		SingleThreadedLockedMapVariable<Double,String, HashMap<Double,String>> map_var_side_a =
				new  SingleThreadedLockedMapVariable<Double,String, HashMap<Double,String>>(host_uuid_a,true);
		
		SingleThreadedLockedMapVariable<Double,String, HashMap<Double,String>> map_var_side_b =
				new  SingleThreadedLockedMapVariable<Double,String, HashMap<Double,String>>(host_uuid_a,true);
		
		Double key_to_use = new Double(39);
		String key_val_to_use = new String("Did it work?");
		map_var_side_a.get_val(null).set_val_on_key(null, key_to_use,key_val_to_use);
		
		var_store_a.add_var(common_var_name, map_var_side_a);
		var_store_b.add_var(common_var_name, map_var_side_b);
		
		// generate the deltas on one side and send them to the other
		VarStoreDeltas.Builder deltas = var_store_a.generate_deltas(null, true);

		
		
		var_store_b.incorporate_deltas(null, deltas.build());
		
		// check that value of b now equals that of a
		SingleThreadedLockedMapVariable<Double,String,HashMap<Double,String>> updated_side_b = 
				(SingleThreadedLockedMapVariable<Double,String,HashMap<Double,String>>)var_store_b.get_var_if_exists(common_var_name);
		
		
		if (! updated_side_b.get_val(null).contains_key_called(null, key_to_use) )
		{
			System.out.println(updated_side_b.get_val(null).get_len(null));
			System.out.println("Side b is missing a key after deserialization.");
			return false;
		}
		
		if (updated_side_b.get_val(null).get_val_on_key(null,key_to_use) != key_val_to_use)
		{
			System.out.println("Side b has incorrect value stuffed into key");
			return false;
		}
		
		// now modify b, and ensure that updates got to other side
		String updated_val = "This is updated";
		Double new_key_to_use = new Double (key_to_use + 1);
		String new_key_to_use_val = "vallll";
		
		updated_side_b.get_val(null).set_val_on_key(null, key_to_use, updated_val);
		updated_side_b.get_val(null).set_val_on_key(null, new_key_to_use, new_key_to_use_val);
		
		// generate deltas and send them to initial side
		VarStoreDeltas.Builder updated_deltas = var_store_b.generate_deltas(null, false);
		var_store_a.incorporate_deltas(null, updated_deltas.build());
		
		// check that changes made it to other side
		SingleThreadedLockedMapVariable<Double,String,HashMap<Double,String>> updated_side_a = 
				(SingleThreadedLockedMapVariable<Double,String,HashMap<Double,String>>)var_store_a.get_var_if_exists(common_var_name);
		
		if (!updated_side_a.get_val(null).contains_key_called(null, new_key_to_use))
		{
			System.out.println("Missing key on a");
			return false;
		}

		if (updated_side_a.get_val(null).get_val_on_key(null, new_key_to_use) != new_key_to_use_val)
		{
			System.out.println("Incorrect val on new key on a");
			return false;
		}
		
		if (updated_side_a.get_val(null).get_val_on_key(null, key_to_use) != updated_val)
		{
			System.out.println("Got incorrect preliminary value");
			return false;
		}
		
		return true;
	}
	

}


