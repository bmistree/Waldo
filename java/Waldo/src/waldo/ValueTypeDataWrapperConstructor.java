package waldo;


public class ValueTypeDataWrapperConstructor<T> extends DataWrapperConstructor<T,T>
{	
	@Override
	public DataWrapper<T,T> construct(T _val, boolean peered) {
		return new ValueTypeDataWrapper<T>(_val,peered);
	}
}
