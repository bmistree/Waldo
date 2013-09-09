package library_tests;

import waldo.LockedObject;
import waldo.LockedVariables;
import waldo.LockedVariables.SingleThreadedLockedMapVariable;
import waldo.SingleThreadedLockedContainer;
import waldo.VariableStore;
import waldo_protobuffs.VarStoreDeltasProto.VarStoreDeltas;

import java.util.ArrayList;
import java.util.HashMap;

import WaldoExceptions.BackoutException;


public class NestedSingleThreadedMapSerializeDeserialize implements TestInterface
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
		return (new NestedSingleThreadedMapSerializeDeserialize()).run_test();
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
		
		
		SingleThreadedLockedMapVariable
			<Double,
			SingleThreadedLockedMapVariable<Double,String,HashMap<Double,String>>,
			HashMap<Double, HashMap<Double,String>>> map_var_side_a =			
				new SingleThreadedLockedMapVariable
				    <Double,
				    SingleThreadedLockedMapVariable<Double,String,HashMap<Double,String>>,
				    HashMap<Double, HashMap<Double,String>>>(host_uuid_a,true);  

		SingleThreadedLockedMapVariable
		<Double,
		SingleThreadedLockedMapVariable<Double,String,HashMap<Double,String>>,
		HashMap<Double, HashMap<Double,String>>> map_var_side_b =			
			new SingleThreadedLockedMapVariable
			    <Double,
			    SingleThreadedLockedMapVariable<Double,String,HashMap<Double,String>>,
			    HashMap<Double, HashMap<Double,String>>>(host_uuid_b,true);  


		// putting a map into a that maps from 69 to wow.
		Double key_to_use = new Double(39);
		Double internal_key_to_use = new Double(key_to_use + 30);
		String internal_val_to_use = "wow";
		SingleThreadedLockedMapVariable<Double,String,HashMap<Double,String>> new_element = 
				new SingleThreadedLockedMapVariable<Double,String,HashMap<Double,String>>(host_uuid_a,false);
		try {
			new_element.get_val(null).set_val_on_key(null, internal_key_to_use,internal_val_to_use);
			map_var_side_a.get_val(null).set_val_on_key(null,key_to_use,new_element);
		} catch (BackoutException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		
		
		var_store_a.add_var(common_var_name, map_var_side_a);
		var_store_b.add_var(common_var_name, map_var_side_b);
		
		// generate the deltas on one side and send them to the other
		VarStoreDeltas.Builder deltas = var_store_a.generate_deltas(null, true);

		
		
		var_store_b.incorporate_deltas(null, deltas.build());
		
		// check that value of b now equals that of a
		

		SingleThreadedLockedMapVariable
			<Double,
			SingleThreadedLockedMapVariable<Double,String,HashMap<Double,String>>,
			HashMap<Double, HashMap<Double,String>>> updated_side_b =
			    (SingleThreadedLockedMapVariable
			    		<Double,
			    		SingleThreadedLockedMapVariable<Double,String,HashMap<Double,String>>,
			    		HashMap<Double, HashMap<Double,String>>>)  var_store_b.get_var_if_exists(common_var_name);
		
		
		
		if (! updated_side_b.get_val(null).contains_key_called(null, key_to_use) )
		{
			System.out.println("Side b is missing a key after deserialization.");
			return false;
		}

		
		if (updated_side_b.get_val(null)
				.get_val_on_key(null, key_to_use)
				.get_val(null)
				.get_val_on_key(null, internal_key_to_use) != internal_val_to_use)
		{
			System.out.println("Side b has incorrect value stuffed into key");
			return false;
		}
		
		
		return true;
	}
	

}


