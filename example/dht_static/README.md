Static DHT
=================

Each DHT node is a single-endpoint connection, defined by Node in node.wld.
Each node holds a local variable store, which maps keys to values, as well as a
finger table that holds connections to other nodes in the DHT graph.  These
connections between nodes are defined in node_connection.wld.


Before a DHT node can join the DHT graph, it must contact a discovery service to
determine which other nodes it should connect to and to register with it.  (The
discovery service is defined as CoordinatorMaster in coordinator_master.wld; and
the connections to and from the CoordinatorMaster are Requester and Coordinator,
each defined in coordinator_connection.wld.)


Following this registration, the DHT node connects to the other node addresses
returned by the discovery service.  Currently, Waldo has no way to initiate the
act of connecting and disconnecting within a transaction.  Therefore, in this
example, we include a mandatory sleep phase between each connecting node.  Note
that except for small topologies, dht nodes do not hold connections to *all*
other nodes in the graph, but rather a subset.

Connections between nodes are symmetric endpoints, defined in
node_connection.wld.  And nodes can request members of their finger tables to
add, remove, and get data through these connections.


setup_dht.py
-----------------
Reads through conf.py and:

  * Starts a discovery service node (CoordinatorMaster)
  * Creates a separate DHT node for each host name, port pair listed
    in conf.py
  * Loads random data into the dht (data generated in data.py, amount
    of data controlled by NUMBER_DATA_ITEMS in conf.py)
  * Queries dht node for data.  Once for each item
  * Prints statistics
  

dht_lib.py
-----------------
Contains helper methods for setting up discovery service and dht
nodes, as well as loading data into a dht node and querying data from
a dht node.


node.wld
----------------
Specifies an individual DHT node.  Maintains a local variable store
for data that are located on it as well as a finger table of other
nodes.  Note that we are currently assuming a static DHT.  Will add
this feature when build dynamic dht.  Node takes in foreign functions
to do some of the heavy lifting for hashing data values


node_connection.wld
-----------------
Each DHT node communicates with partners in its finger table.  It does
so using a symmetric protocol defined in node_connection.wld.


coordinator_master.wld
-----------------
Defines CoordinatorMaster, the discovery service for connecting nodes.


coordinator_connection.wld
-----------------
To register DHT node and communicate with CoordinatorMaster, use
protocol described in this file.


Build + Run
-----------------
To build:
make

To run:
python setup_dht.py


