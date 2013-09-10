package library_tests;

public class AllTests 
{
	
	public static void run_single_test(String test_description,TestInterface to_run)
	{
		if (to_run.run_test())
			test_description += ".... Success";
		else
			test_description += ".... Fail";
		System.out.println(test_description + "\n");
	}
	
	public static void main(String[] args) 
	{
		
		run_single_test(
				"Testing getters and setters on single threaded map keys",
				new BasicSingleThreadedMapTest());
		
		run_single_test(
				"Testing getters and setters on single threaded number",
				new BasicSingleThreadedNumber());
		
		run_single_test(
				"Testing serializing and deserializing single threaded number",
				new SingleThreadedNumberSerializeDeserialize());
				
		run_single_test(
				"Testing serializing and deserializing single threaded map",
				new SingleThreadedMapSerializeDeserialize());
				
		run_single_test(
				"Nested serializing and deserializing single threaded map",
				new NestedSingleThreadedMapSerializeDeserialize());
		
		run_single_test(
				"Multithreaded concurrent read of number",
				new MultithreadedNoConflict());

		run_single_test(
				"Multithreaded full read/write/commit number",
				new MultiThreadedCommit());
		
		
		run_single_test(
				"Multithreaded conflict number",
				new MultiThreadedConflict());
				
		
	}


}
