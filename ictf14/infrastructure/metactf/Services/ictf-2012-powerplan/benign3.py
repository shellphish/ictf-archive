""" 
Benign traffic Description:
  Connect => New game => Random play with gaussian distribution => Exit
"""
import random
import re
from socket import socket
import string
import sys
import time

class Benign():

    DEFAULT_ERROR_CODE = 42 
    call_interval = 60 
    call_interval_sd = 10

    def execute(self, ip, port, flag_id, token):

        def get_random_user_id():
            return ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(10))

        def get_random_passwd():
            return ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(16))

        def get_victory_msg():
            msgLength = random.randrange(20, 250)
            return ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(msgLength))

        user_id = get_random_user_id()
        passwd = get_random_passwd()
        # An error code of -1 means the service is down
        self.error = -1
        self.error_msg = ''
        try:
            self.sock = socket()
            self.sock.connect((ip, port))
            self.sock_file = self.sock.makefile()
            # We connected successfuly, so set the error code back to default
            self.error = self.DEFAULT_ERROR_CODE
            self.wait_for_regex(r"^create new user or login")
            self.send_msg("N")
            self.wait_for_regex(r"^user name")
            self.send_msg(user_id)
            self.wait_for_regex(r"^create a password")
            self.send_msg(passwd)

            # Get board
            board = self.wait_for_regex(r"^([-*\d]\s+){4}[-*\d]") + "\n"
            board += self.recv_msg() + "\n"
            board += self.recv_msg() + "\n"
            board += self.recv_msg() + "\n"
            board += self.recv_msg() + "\n"
            board = Board(board_str = board)
            while True:
                possibleMoves = ["S", "SE", "E", "NE", "N", "NW", "W", "SW"]
                random.shuffle(possibleMoves)
                self.send_msg(possibleMoves[0])
                msg = self.recv_msg()
                if "discovered" in msg:
                    break
                else:
                    self.wait_for_regex(r"^Select a move")

            # Everything worked. Set error to 0
            self.error = 0
            
        except Exception as e:
            self.error_msg = str(e)

    """
    Blocks until data is received that matches the given regex
    """
    def wait_for_regex(self, regex):
        compiled_regex = re.compile(regex)
        while True:
            data = self.sock_file.readline()
            print "Received: {0}".format(data.strip())
            if(len(data)==0):
                raise Exception("Exit")
            elif (compiled_regex.match(data)):
              return data.strip()

    def send_msg(self, data):
        time.sleep(abs(random.gauss(1, .5)))
        self.sock.sendall(data + "\n")
    
    def recv_msg(self):
        data = self.sock_file.readline()
        print "Received: {0}".format(data.strip())
        if(len(data)==0):
            raise Exception("Exit")
        return data.strip()

    def result(self):
        return {'ERROR' : self.error,
                'ERROR_MSG' : self.error_msg,
               }


class Board:

    def __init__(self,w=6,h=6,board_str=""):
        if board_str!="":
            board_str = board_str.strip()
            w = len(board_str.split("\n"))
            h = len(board_str.split("\n")[0].split())
            self.wsize = w
            self.hsize = h
            self.board_table = [[-1 for x in xrange(self.hsize)] for x in xrange(self.wsize)]
            self.ncells = w*h
            self.nblocks = 0
            self.block_for_solution = self.ncells 
            maxv = -1
            last_ci,last_cj = 0,0
            for i,line in enumerate(board_str.split("\n")):
                for j,cell_str in enumerate(line.split()):
                    v = self.string_to_cell(cell_str)
                    self.board_table[i][j] = v
                    if(v == -1):
                        self.set_block(i, j)
                    if(v >= maxv):
                        maxv = v
                        last_ci,last_cj = i,j
            self.last_v = maxv
            self.last_ci = last_ci
            self.last_cj = last_cj
            
        else:
            self.wsize = w
            self.hsize = h
            self.board_table = [[-1 for x in xrange(self.hsize)] for x in xrange(self.wsize)] 
            self.ncells = w*h
            self.last_v = 0
            self.last_ci = 0
            self.last_cj = 0
            self.nblocks = 0
            self.block_for_solution = self.ncells
            for i in xrange(self.wsize):
                for j in xrange(self.hsize):
                    self.board_table[i][j] = 0
                
    def set_initial_position(self,i,j):
        self.last_v += 1
        self.board_table[i][j] = self.last_v
        self.last_ci, self.last_cj = i,j
                
    def move_to_ij(self,p):
        if(p=="S"):
            return 3,0
        elif(p=="SE"):
            return 2,2
        elif(p=="E"):
            return 0,3
        elif(p=="NE"):
            return -2,2
        elif(p=="N"):
            return -3,0
        elif(p=="NW"):
            return -2,-2
        elif(p=="W"):
            return 0,-3
        elif(p=="SW"):
            return 2,-2
                
    def check_and_add_move(self,p):
        i,j = self.move_to_ij(p)
            
        new_ci, new_cj = self.last_ci + i, self.last_cj + j
        if(new_ci < 0 or new_cj < 0 or new_ci >= self.wsize or new_cj >= self.hsize):
            return False
        if (self.board_table[new_ci][new_cj] == 0):
            self.last_v += 1
            self.board_table[new_ci][new_cj] = self.last_v
            self.last_ci, self.last_cj = new_ci, new_cj
            return True
        else:
            return False
        
    def remove_move(self,p):
        i,j = self.move_to_ij(p)
        
        self.board_table[self.last_ci][self.last_cj] = 0
        new_ci, new_cj = self.last_ci - i, self.last_cj - j
        self.last_v -= 1
        self.last_ci, self.last_cj = new_ci, new_cj
        
    def set_block(self,i,j):
        self.board_table[i][j] = -1
        self.nblocks += 1
        self.block_for_solution -= 1
        
    def is_solved(self):
        if (self.last_v == self.block_for_solution):
            return True
        else:
            return False
        
    def get_solution_list(self,to_be_removed=0):
        to_be_removed = max(to_be_removed-1,0)
        
        solution_list = []
        for i in xrange(self.wsize):
            for j in xrange(self.hsize):
                if(self.board_table[i][j] == 1):
                    ci,cj = i,j
                    break
            else:
                continue  # executed if the loop ended normally (no break)
            break
        else:
            return solution_list
        
        cv = 2
        while(cv <= self.block_for_solution):
            for m in ["S", "SE", "E", "NE", "N", "NW", "W", "SW"]:
                i,j = self.move_to_ij(m)
                ni,nj = ci+i,cj+j
                if(ni<0 or nj<0 or ni>=self.wsize or nj >=self.hsize):
                    continue
                if(self.board_table[ci+i][cj+j] == cv):
                    ci,cj = ni,nj
                    cv += 1
                    solution_list.append(m)
                    break;
            else:
                return solution_list[to_be_removed:]
        return solution_list[to_be_removed:]
                 
    def solve(self):
        moves =  ["S", "SE", "E", "NE", "N", "NW", "W", "SW"]
        random.shuffle(moves)
        for m in moves:
            r = self.check_and_add_move(m)
            if(r):
                self.solve()
                if(self.is_solved()):
                    return
                #print repr(br)
                self.remove_move(m)
            else:
                pass
                
    def string_to_cell(self,cstr):
        if("*" in cstr):
            return -1
        elif("-" in cstr):
            return 0
        else:
            return int(cstr)
                
    def cell_to_string(self,v):
        if(v == -1):
            return " *"
        elif(v == 0):
            return " -"
        else:
            return "%2d" % v
        
    def check(self):
        return True
        
    def __repr__(self):
        tstr = ""
        for i in xrange(0,self.wsize):
            for j in xrange(0,self.hsize):
                tstr +=" " + self.cell_to_string(self.board_table[i][j]) + " " 
            tstr += "\n"       
        return tstr
    
    
    #FIXME remove methods unused by server code (e.g. solve() )
    #but we need these methods for exploit1.py!
    
