from omid_server_emitted import OmidServer
from omid_player_emitted import OmidPlayerHelper
import sys, os, time
sys.path.append(os.path.join("../../"))
from waldo.lib import Waldo
OMID_FILE = "omid_game_data.txt"
NODE_DIVIDER = "--NODES--"
ARC_DIVIDER = "--ARCS--"
GAME_DIVIDER = "-----GAME-----"
DELIMITER = " -- "
NODE_FIELD_0 = "answer"
NODE_FIELD_1 = "node_num"
NODE_FIELD_2 = "x"
NODE_FIELD_3 = "y"
NODE_FIELD_4 = "found"
ARC_FIELD_1 = "node1"
ARC_FIELD_2 = "node2"
END = ""
OMID_PORT = 6770

def load_game_info():
    game_file = open(OMID_FILE, 'r', 0)
    global nodes
    global arcs
    nodes = {}
    arcs = []
    while True:
        line = game_file.readline().rstrip()
        if line == NODE_DIVIDER:
            line = game_file.readline().rstrip()
            while line != ARC_DIVIDER:
                split_line = line.split(DELIMITER)
                node_struct = {}
                node_struct[NODE_FIELD_0] = split_line[0]
                node_struct[NODE_FIELD_1] = split_line[1]
                node_struct[NODE_FIELD_2] = int(split_line[2])
                node_struct[NODE_FIELD_3] = int(split_line[3])
                node_struct[NODE_FIELD_4] = True if split_line[4] == "T" else False
                nodes[split_line[0]] = node_struct
                line = game_file.readline().rstrip()
            line = game_file.readline().rstrip()
            while line != "" and line != GAME_DIVIDER:
                split_line = line.split(DELIMITER)
                arc_struct = {}
                arc_struct[ARC_FIELD_1] = split_line[0]
                arc_struct[ARC_FIELD_2] = split_line[1]
                arcs.append(arc_struct)
                line = game_file.readline().rstrip()
            if line == "":
                break
                
load_game_info()
omid_server = Waldo.no_partner_create(OmidServer)
omid_server.set_map(nodes, arcs)
Waldo.tcp_accept(OmidPlayerHelper, '127.0.0.1', OMID_PORT, omid_server)
while True:
    print 'Waiting for omid players'
    while omid_server.get_player_count() <= 0:
        time.sleep(0.1)
    omid_server.broadcastWaitingMessage('Game will begin in 10 seconds. Type "/ready" to join.\n')
    time.sleep(3)
    omid_server.start_game()
    time.sleep(60)
    omid_server.end_game()
