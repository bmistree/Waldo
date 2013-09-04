package waldo;

public interface MultiThreadedConstructor<T> {
	public MultiThreadedLockedObject<T> construct(String host_uuid, boolean peered, Object init_val);
}
