package waldo;

import java.util.List;
import java.util.ArrayList;
import java.util.HashMap;

public class Util {
	
	/**
	 * Queues must be declared with capacities.  All queues have this default capacity
	 */
	static public int QUEUE_CAPACITIES = 100;

	/**
	 * 	Takes in the name of the function that another endpoint has
	    requested to be called.  Adds a prefix to distinguish the function
	    as being called from an endpoint function call rather than from
	    external code.
	*/
	static public String endpoint_call_func_name(String func_name)
	{
		return "_endpoint_func_call_prefix__waldo__" + func_name;
	}
	

	/**
	 * 	@see endpoint_call_func_name, except as a result of partner
	    sending a message in a message sequence.
	 * @param func_name
	 * @return
	 */
	static public String partner_endpoint_msg_call_func_name(String func_name)
	{
	    return "_partner_endpoint_msg_func_call_prefix__waldo__" + func_name;
	}

	

	static public String internal_oncreate_func_call_name(String func_name)
	{
	    return "_onCreate";
	}

	static public String generate_uuid()
	{
		return java.util.UUID.randomUUID().toString();
	}
	
	static public void logger_assert(String to_assert)
	{
		System.out.println("Compiler error: " + to_assert);
		assert(false);
	}
	
	static public void logger_warn(String to_warn)
	{
		System.out.println("Compiler warn: " + to_warn);		
	}
	
	
}
