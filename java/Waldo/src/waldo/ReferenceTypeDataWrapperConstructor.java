package waldo;

import java.util.HashMap;

/**
 * 
 * @author bmistree
 *
 * key, value, returned from dewaldoify
 *
 * @param <K> --- Key for the map
 * @param <V> --- Java variables in the hashmap
 */

public class ReferenceTypeDataWrapperConstructor<K,V> 	
	extends DataWrapperConstructor<
        // The actual internal data that will be held by the data wrapper
        HashMap<K,LockedObject<V>>, 
    	// what you get when you call dewaldoify on the data wrapper
    	HashMap<K,V> >
{

	@Override
	public DataWrapper<HashMap<K, LockedObject<V>>, 
						HashMap<K,V>>
    construct(
			HashMap<K, LockedObject<V>> _val, boolean peered) 
	{
		return new ReferenceTypeDataWrapper<K,V>(_val,peered);
	}
	
}

