package waldo;

import java.util.HashMap;

public class SingleThreadedLockedInternalMapVariable<K,V,D> extends
		SingleThreadedLockedContainer<K,V,D>
{

	public SingleThreadedLockedInternalMapVariable(
			String _host_uuid,boolean _peered,HashMap<K,LockedObject<V,D>> init_val)
	{
		super();
		ReferenceTypeDataWrapperConstructor<K,V,D>rtdwc = new ReferenceTypeDataWrapperConstructor<K,V,D>();
		init(_host_uuid,_peered,rtdwc,init_val);
	}
	public SingleThreadedLockedInternalMapVariable(
			String _host_uuid,boolean _peered)
	{
		super();
		ReferenceTypeDataWrapperConstructor<K,V,D>rtdwc = new ReferenceTypeDataWrapperConstructor<K,V,D>();
		HashMap<K,LockedObject<V,D>> init_val = new HashMap<K,LockedObject<V,D>>();
		init(_host_uuid,_peered,rtdwc,init_val);
	}

}
