package waldo;

public class DataWrapperConstructor<T> {
	public DataWrapper<T> construct(T _val, boolean peered)
	{
		return new DataWrapper<T>(_val,peered);
	}
	
}
