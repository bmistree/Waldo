Waldo
================

Waldo is a domain specific language for writing application protocols.
Waldo wraps protocol data and logic from two endpoints in a single
file, which gets transcompiled into code that can be used by an
application.

Waldo's key features map to challenges observed from programmers
writing distributed applications:

  * Waldo provides an atomic event model, in which programmers can
compose operations across multiple hosts into a single, atomic event.
This atomicity reduces protocol edge cases by shrinking a protocol's
visible state space: instead of considering all possible interleavings
of messages and expressions, a programmer need only reason about
orderings of high-level events.

  * Waldo programmers do not explicitly synchronize state themselves.
Waldo's type system includes replication types.  Using replication
types, the Waldo runtime automatically synchronizes state between
endpoints and schedules events to avoid read-write conflicts.

  * Waldo fails fast on events interrupted by network or node
failure, throwing an exception.  Through replication types, Waldo
exposes what data are available on a host during exception handling.

Waldo is an adolescent language and not all of the above works well
(or even works!).  For known issues or to file a bug, see the github
page [here] (https://github.com/bmistree/Waldo/issues?state=open).

For API documentation of the Waldo module, go [here]
(http://bcoli.stanford.edu/wdoc/).


Installation
----------------
If you have installed correctly, running test/runAllTests.py from the
command line should produce all SUCCESS-es.


Running
----------------

    bin/wcompile.py -f <waldo filename> -e <python file to emit to>

or to automatically emit to emitted.py:

    bin/wcompile.py <waldo filename> 

For compile options:

    bin/wcompile.py -h 

For example Makefiles, see test/emit_tests/Makefile or
example/*/Makefile.

