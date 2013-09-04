package waldo;

public interface SingleThreadedConstructor<T> {
	public SingleThreadedLockedObject<T> construct(String host_uuid, boolean peered, Object init_val);
}
