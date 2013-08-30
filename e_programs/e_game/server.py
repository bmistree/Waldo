from user_login_emitted import UserLoginHelper
from user_emitted import UserHelper
from player_emitted import PlayerHelper
from anagram_server_emitted import AnagramServer
from server_emitted import Server
from omid_server_emitted import OmidServer
from omid_player_emitted import OmidPlayerHelper
from password_server_emitted import PasswordServer
from optparse import OptionParser
import sys, os, time, random, thread
from login import LoginWindow
import ssl
sys.path.append(os.path.join("../../"))
from waldo.lib import Waldo

HOSTNAME = '127.0.0.1'
PORT = 6922
ANAGRAM_PORT = 6767
ANAGRAM_WAITTIME = 10
GAMETIME = 60
FILENAME = 'database.txt'
SOLUTION_FILENAME = 'solutions.txt'
database = {}
STRUCT_FIELD_ONE = "hashed_password"
STRUCT_FIELD_TWO = "encryptKey"
STRUCT_FIELD_THREE = "cert"
STRUCT_FIELD_FOUR = "salt"
STRUCT_FIELD_FIVE = "type"
USER_SEP = "\n----------END USER----------\n\n----------BEGIN USER----------\n"
KEY_MANAGER_PORT = 6974
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

def start_omid_server():
    load_game_info()
    omid_server = Waldo.no_partner_create(OmidServer)
    omid_server.set_map(nodes, arcs)
    Waldo.tcp_accept(OmidPlayerHelper, HOSTNAME, OMID_PORT, omid_server)
    while True:
        print 'Waiting for omid players'
        while omid_server.get_player_count() <= 0:
            time.sleep(0.1)
        omid_server.broadcastWaitingMessage('Game will begin in 10 seconds. Type "/ready" to join.\n')
        time.sleep(10)
        omid_server.start_game()
        time.sleep(60)
        omid_server.end_game()
        

def hasher(event, password, salt):
    return Waldo.hash(password, salt)

def load_database():
    database_file = open(FILENAME, 'r', 0)
    users = database_file.read().split(USER_SEP)
    for line in users:
        if (len(line) > 0):
            split_line = line.split(DELIMITER)
            global database
            user_info = {}
            user_info[STRUCT_FIELD_ONE] = split_line[1]
            user_info[STRUCT_FIELD_TWO] = split_line[2]
            user_info[STRUCT_FIELD_THREE] = split_line[3]
            user_info[STRUCT_FIELD_FOUR] = split_line[4]
            database[split_line[0]] = user_info
    database_file.close()

def save_database(endpoint, user_dict):
    database_file = open(FILENAME, 'w', 0)
    for user in user_dict:
        user_info = user_dict[user]
        line = user + DELIMITER + user_info[STRUCT_FIELD_ONE] + DELIMITER + user_info[STRUCT_FIELD_TWO] + DELIMITER + user_info[STRUCT_FIELD_THREE] + DELIMITER + user_info[STRUCT_FIELD_FOUR] + USER_SEP
        database_file.write(line)
    database_file.close()


def create_password_server():
    password_server = Waldo.no_partner_create(PasswordServer, Waldo.get_ca_endpoint(HOSTNAME, KEY_MANAGER_PORT), database, save_database, hasher)
    Waldo.stcp_accept(UserLoginHelper, HOSTNAME, PORT + 1, password_server)
    return password_server

def create_server():
    server = Waldo.no_partner_create(Server)
    Waldo.stcp_accept(UserHelper, HOSTNAME, PORT, server, cert_reqs= ssl.CERT_OPTIONAL, ca_certs = "ca_list.pem")

def load_solutions():
    solution_file = open(SOLUTION_FILENAME, 'r', 0)
    solutions = solution_file.read().splitlines()
    solution_file.close()
    anagram = ""
    solution = []
    global solution_set
    solution_set = {}
    for line in solutions:
        if line == "":
            solution_set[anagram] = solution
            solution = []
        elif line.startswith('--'):
            anagram = line[2:].upper()
        else:
            solution.append(line.upper())

def set_solutions(anagram_server):
    anagram = random.choice([key for key in solution_set])
    solutions = solution_set[anagram]
    anagram_server.set_solution(anagram, solutions)

def run_anagram_server():
    anagram_server = Waldo.no_partner_create(AnagramServer)
    Waldo.tcp_accept(PlayerHelper, HOSTNAME, ANAGRAM_PORT, anagram_server)
    load_solutions()
    while True:
        print 'Waiting for players....'
        while anagram_server.get_player_count() <= 0:
            time.sleep(0.1)
        print 'Player entered.  Game will begin in 10 seconds.'
        set_solutions(anagram_server)
        anagram_server.broadcastWaitingMessage('Game will begin in %d seconds. Type "/ready" to join.\n' %ANAGRAM_WAITTIME)
        for i in range(ANAGRAM_WAITTIME):
            if (i == ANAGRAM_WAITTIME/2):
                anagram_server.broadcastMessage('Game will begin in %d seconds\n' %i)
            time.sleep(1)
        print 'Game has begun!'
        anagram_server.start_game()
        time.sleep(20)#Change to GAMETIME after testing
        anagram_server.end_game()
        time.sleep(ANAGRAM_WAITTIME/2)
        anagram_server.restart_server()
    

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-g", "--generate", action ="store_true", dest = "generate", default = False)
    (option, args) = parser.parse_args()
    Waldo.start_ca(option.generate, host = HOSTNAME, port = KEY_MANAGER_PORT, cert_end = 60*60*24*365)
    if option.generate:
        Waldo.add_ca_to_list("ca_list.pem", HOSTNAME, KEY_MANAGER_PORT)
    load_database()
    password_server = create_password_server()
    create_server()
    thread.start_new_thread(run_anagram_server, ())
    thread.start_new_thread(start_omid_server, ())
    while raw_input("Type 'close' to close the server.\n") != 'close':
        pass
    password_server.close()
        
