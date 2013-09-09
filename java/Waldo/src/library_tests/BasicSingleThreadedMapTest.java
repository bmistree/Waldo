package library_tests;

import java.util.HashMap;

import WaldoExceptions.BackoutException;
import waldo.LockedVariables;

/**
 * Simply creates a single threaded map, tries setting some of its values, tries calling len, 
 * tries deleting some of its values, etc.
 * @author bmistree
 *
 */

public class BasicSingleThreadedMapTest implements TestInterface{

	public static void main(String[] args) 
	{
		if (run_static_test())
			System.out.println("\nSucceeded\n");
		else
			System.out.println("\nFailed\n");
				
	}
	
	public static boolean run_static_test()
	{
		return (new BasicSingleThreadedMapTest()).run_test();
	}
	
	public boolean run_test()
	{
		String host_uuid = "some_host_uuid";
		
		// Create a map of strings to Numbers
		LockedVariables.SingleThreadedLockedMapVariable <String,Double, HashMap<String,Double>> string_to_num_map = new
				LockedVariables.SingleThreadedLockedMapVariable<String,Double,HashMap<String,Double>>(host_uuid, false);
		
		String key_to_set_on = "hi";
		Double val_to_set_on_key = new Double(3);
		try {
			string_to_num_map.get_val(null).set_val_on_key(null, key_to_set_on, val_to_set_on_key);
		} catch (BackoutException e) {
			e.printStackTrace();
			return false;
		}
		
		// check that length should be 1
		if (string_to_num_map.get_val(null).get_len(null) != 1)
		{
			System.out.println("Got incorrect length.");
			return false;
		}
		
		// check that got back value that put in on key.
		if (string_to_num_map.get_val(null).get_val_on_key(null, key_to_set_on) != val_to_set_on_key)
		{
			System.out.println("Got incorrect value back");
			return false;
		}
		
		// update value on key:
		Double new_val_on_key = new Double (4);
		try {
			string_to_num_map.get_val(null).set_val_on_key(null, key_to_set_on, new_val_on_key);
		} catch (BackoutException e) {
			e.printStackTrace();
			return false;
		}
		if (string_to_num_map.get_val(null).get_val_on_key(null, key_to_set_on) != new_val_on_key)
		{
			System.out.println("Got incorrect value back after overwriting");
			return false;
		}
		

		// delete val on key
		string_to_num_map.get_val(null).del_key_called(null, key_to_set_on);
		if (string_to_num_map.get_val(null).contains_key_called(null, key_to_set_on))
		{
			System.out.println("Couldn't delete val in map.");
			return false;
		}
		
		return true;
	}
	

}
