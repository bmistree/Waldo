package waldo;

public abstract class DataWrapperConstructor<T> {
	public abstract DataWrapper<T> construct(T _val, boolean peered);	
}
