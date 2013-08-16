from player_emitted import PlayerHelper
from anagram_server_emitted import AnagramServer
import sys, os, time, random
sys.path.append(os.path.join("../../"))
from waldo.lib import Waldo
HOSTNAME = '127.0.0.1'
PLAYER_NUM = 1
GAMETIME = 60
WAITTIME = 10
FILENAME = 'solutions.txt'
SOLUTION_START_INDEX = 1

global solution_set

def load_solutions():
    solution_file = open(FILENAME, 'r', 0)
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


if __name__ == '__main__':
    anagram_server = Waldo.no_partner_create(AnagramServer)
    print 'GameServer created!'
    Waldo.tcp_accept(PlayerHelper, HOSTNAME, 6767, anagram_server)
    load_solutions()
    while True:
        print 'Waiting for players....'
        while anagram_server.get_player_count() <= 0:
            time.sleep(0.1)
        print 'Player entered.  Game will begin in 10 seconds.'
        set_solutions(anagram_server)
        anagram_server.broadcastWaitingMessage('Game will begin in %d seconds. Type "/ready" to join.\n' %WAITTIME)
        for i in range(WAITTIME):
            if (i == WAITTIME/2):
                anagram_server.broadcastMessage('Game will begin in %d seconds' %i)
            time.sleep(1)
        print 'Game has begun!'
        anagram_server.start_game()
        time.sleep(20)
        anagram_server.end_game()
        time.sleep(WAITTIME/2)
        anagram_server.restart_server()
    
