package library_tests;

import waldo.LockedVariables;
import waldo.LockedVariables.SingleThreadedLockedNumberVariable;

public class BasicSingleThreadedNumber implements TestInterface
{
	/**
	 * Tests that can perform basic sets and gets on single threaded number variable.
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
		return (new BasicSingleThreadedNumber()).run_test();
	}
	
	
	public boolean run_test()
	{
		SingleThreadedLockedNumberVariable num_var = 
				new LockedVariables.SingleThreadedLockedNumberVariable("dummy_host",false,null);
			
		Number num = num_var.get_val(null);
		if (num.doubleValue() != 0)
		{
			System.out.println("Incorrect default value");
			return false;
		}
		double num_to_set_to = 303;
		num_var.set_val(null,num_to_set_to);
		num = num_var.get_val(null);
		if (num.doubleValue() != num_to_set_to)
		{
			System.out.println("Incorrect set value");
			return false;
		}
		
		
		return true;
	}
	

}
