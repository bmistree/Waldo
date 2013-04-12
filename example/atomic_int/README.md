AtomicInt
=====================

Although Waldo is intended for scripting behavior across two or more
endpoints, it can also be used on just a single endpoint to provide
transactions on local state.  In this example, we created a simple
atomic integer "endpoint."  In Waldo projects, single endpoint files
can also be useful, for instance, if you have some manager holding
references to multiple connections, which share the manager's data.
For an exmaple of this, see the dht example.

In this test, we create 100 threads, each of which tries to increment
a shared atomic integer.  After all threads have run, prints the final
value of the atomic integer (which should be 100).

Note: this test runs slowly because Waldo is missing a sensible retry
policy: as soon as a conflict is detected, each thread tries to retry
its event instantly.


Build + Run
---------------------
To build, type 
make

To run,
python atomic_int_test.py


