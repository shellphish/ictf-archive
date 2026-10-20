#! /usr/bin/env python

import SocketServer
import threading
import base64
import cPickle
import sys
import time
import shutil
import os
import re
import base64
import hashlib
import time
import cPickle
import subprocess
from Board import Board
import random

save_folder = "saves"

class MyTCPHandler(SocketServer.StreamRequestHandler):
    
    def recv_msg(self):
        data = self.rfile.readline()
        if(len(data)==0):
            sys.exit(1)
            
        return data.strip()

    def send_msg(self, data):
        self.wfile.write(data + "\n")
        
    def ask_question(self,question,options):
        option_str = "/".join(options)
        tstr = question + " [%s]" % option_str
        self.send_msg(tstr)
        rmesg = self.recv_msg()
        while(rmesg not in options):
            self.send_msg("Invalid input, valid options: [%s]" % option_str)
            rmesg = self.recv_msg()
        return rmesg
        
    def ask_regex(self,question,regex):
        compiled_regex = re.compile(regex)
        self.send_msg(question)
        rmesg = self.recv_msg()
        while(not compiled_regex.match(rmesg)):
            self.send_msg("Invalid input")
            rmesg = self.recv_msg()
        return rmesg
        
    def check_login(self,user_name,passwd):
        file_name = base64.urlsafe_b64encode(user_name)
        if(os.path.exists(os.path.join(save_folder,file_name))):
            fp = open(os.path.join(save_folder,file_name))
            file_content = fp.read()
            fp.close()
            saved_passwd = file_content.split("\n")[0]
            if(hashlib.sha256(passwd).hexdigest() == saved_passwd):
                return True
        return False
    
    def send_board(self,board):
        tstr = repr(board)
        for line in tstr.split("\n"):
            self.send_msg(line.strip())
            
    def load_board(self,user_name):
        #bad programming, this is going to fail if trying to load a file with only the password, or a file with a victory message
        file_name = base64.urlsafe_b64encode(user_name)
        fp = open(os.path.join(save_folder,file_name))
        file_content = fp.read()
        fp.close()
        file_content.split("\n")[1]
        board = cPickle.loads(base64.b64decode(file_content.split("\n")[1]))
        if(board.check() != True): #make it fail when exploit is used
            raise Exception("tried to load a malformed board")
        else:
            return board
        
    def load_score(self,user_name):
        #bad programming, this is going to fail if trying to load a file with only the password, or a file with a board
        file_name = base64.urlsafe_b64encode(user_name)
        fp = open(os.path.join(save_folder,file_name))
        file_content = fp.read()
        fp.close()
        victory_message = file_content.split("\n")[1]
        score = int(file_content.split("\n")[2]) #make it fail 
        return (victory_message,score)
    
    def save_board(self,file_name,passwd,board):
        hashed_passwd = hashlib.sha256(passwd).hexdigest()
        tstr = "{0}\n{1}\n".format(hashed_passwd,base64.b64encode(cPickle.dumps(board)))
        fp = open(os.path.join(save_folder,file_name),"wb")
        fp.write(tstr)
        fp.close()   
        
    def save_score(self,file_name,passwd,victory_message,score):
        hashed_passwd = hashlib.sha256(passwd).hexdigest()
        tstr = "{0}\n{1}\n{2}\n".format(hashed_passwd,victory_message,score)
        fp = open(os.path.join(save_folder,file_name),"wb")
        fp.write(tstr)
        fp.close()            
    
    def ask_continue(self):
        res = self.ask_question("Do you want to continue? ", ["Y","N"])
        if(res == "N"):
            sys.exit(0)
    
    def handle(self):
        print "* start handling a connection *"
        try:
            self.internal_handle()
        except KeyboardInterrupt:
            pass
        except SystemExit:
            pass
        print "* stop handling a connection *"
        
    def internal_handle(self):
        res = self.ask_question("create new user or login",["N","L"])
        user_name = ""
        file_name = ""
        if(res == "N"):
            #FIXME set max len based on flag-id size
            user_name = self.ask_regex("user name",r"^[a-zA-Z0-9_]{1,100}$")
            file_name = base64.urlsafe_b64encode(user_name)
            if(os.path.exists(os.path.join(save_folder,file_name))):
                self.send_msg("Username not available")
                return
            else:
                #print "Saving file {0} for user {1}".format(file_name, user_name)
                # Request a password
                passwd = self.ask_regex("create a password",r"^[a-zA-Z0-9_]{1,100}$")
                hashed_passwd = hashlib.sha256(passwd).hexdigest()
                # Store the password as the first line in the file
                with open(os.path.join(save_folder, file_name), 'w') as f:
                    f.write(hashed_passwd + "\n")
        else:
            #FIXME set max len based on flag-id size
            user_name = self.ask_regex("user name:",r"^[a-zA-Z0-9_]{1,100}$")
            passwd = self.ask_regex("password:",r"^[a-zA-Z0-9_]{1,100}$")
            file_name = base64.urlsafe_b64encode(user_name)
            if(not self.check_login(user_name, passwd)):
                self.send_msg("Invalid username or password")
                return
        
            # print "New game started for user {0}".format(user_name)
            # Operation Power Plan - Sabotaging the enemey's power grid
            #
            # Your agents have already infilitrated one enemy power plant and shut it down.
            # Your mission: Shut down as many power plants as possible without being discovered 
            # 
            # Your agent will be discovered if they ever try revisiting a previously 
            # shutdown power plant or go off the grid.
            # Remember: One power plant is full of enemy spies. Do not try to shut this down.
            # 

            # Your agent can move among powerplants using 8 different moves. 
            # Tip: Learn quickly how the agent responds to directions, it might not be 
            # what you think. 

            # Direct your agent using the provided controls
            # 0 - S. 1 - SE, 2 - E, 3 - NE, 4 - N, 5 - NW, 6 - W, 7 - SW

            # And since this is only a simulation, you may of course Save your progress with S. 

        self.send_msg("\nOperation Power Plan - Sabotaging the enemy's power grid\n")
        self.send_msg("Your agents have already infiltrated 1 enemy power plant and shut it down.")
        self.send_msg("Your mission: Shut down as many power plants as possible without being discovered.")
        self.send_msg("Your agent will be discovered if they ever try revisiting a previously shutdown")
        self.send_msg("power plant or go off the grid.\n")
        self.send_msg("Remember: One power plant is full of enemy spies.") 
        self.send_msg("Do not to shut down this plant down\n")
        self.send_msg("Your agent can move among powerplants using 8 different moves.")
        self.send_msg("Tip: Learn quickly how the agent responds to directions.\n") 
        self.send_msg("Map Legend:")
        self.send_msg("* : power plant full of enemy spies. Avoid!")
        self.send_msg("- : A power plant that still needs to be infiltrated")
        self.send_msg("Highest number : Your agent's current location\n")
        self.send_msg("And if you would like to take a break, type Save.\n")
            
        while(True):
            board = None
            victory_message,high_score = None,None
            mode = 0
            try:
                loaded_board = self.load_board(user_name)
                mode = 1
            except Exception,e: #FIXME printing exception for debugging, remove this before submitting
                try:
                    victory_message,high_score = self.load_score(user_name)
                    high_score = str(high_score)
                    mode = 2
                except Exception,e: #FIXME printing exception for debugging, remove this before submitting
                    pass
            
            if(mode == 2):
                self.send_msg("Your previous high score was:")
                self.send_msg(high_score)
                self.send_msg("Your previous victory message was:")
                self.send_msg(victory_message)
            
            if(mode == 1):
                res = self.ask_question("Saved board found, do you want to load it? ", ["Y","N"])
                if(res == "Y"):
                    board = loaded_board
        
            if(board == None):
                #FIXME create a board of 6x6, starting from a random position
                #with a single block in a random position
                #board = Board(6,3)
                #board.set_initial_position(0,0)
                #board.set_block(1,0)
                #board.set_block(2,0)
                #board.set_block(4,0)
                #board.set_block(5,0)
                #board.set_block(0,1)
                #board.set_block(1,1)
                #board.set_block(2,1)
                #board.set_block(3,1)
                #board.set_block(4,1)
                #board.set_block(5,1)
                #board.set_block(0,2)
                #board.set_block(1,2)
                #board.set_block(2,2)
                #board.set_block(3,2)
                #board.set_block(4,2)
                #the solution for this board is [0,1]
                board = Board(5, 5)
                # Use the default time
                random.seed(None)
                initial_pos = (random.randrange(0,5), random.randrange(0, 5))
                board.set_initial_position(initial_pos[0], initial_pos[1])
                random_block = None
                ## Pick a random block
                while True:
                    random_block = (random.randrange(0,5), random.randrange(0, 5))
                    if random_block != initial_pos:
                        break;

                board.set_block(random_block[0], random_block[1])
            
            numMoves=0
            current_time = time.time()
            while(not board.is_solved()):
                self.send_board(board)
                move = self.ask_question("Select a move",["S","SE","E","NE","N","NW","W","SW","Save"])
                if(move == "Save"):
                    self.save_board(file_name,passwd,board)
                    self.send_msg("Board saved!")
                    self.ask_continue()
                    break
                else:
                    numMoves += 1
                    res = board.check_and_add_move(move)
                    if(res == False):
                        self.send_msg("You have been discovered!")
                        sys,exit(2)
            else:
                completition_time = time.time() - current_time
                score = str(int(1000000/completition_time) * numMoves)
                self.send_msg("Congratulations! Your score is: {0}".format(score))
                #FIXME size of the regex, exploit goes here!
                victory_message = self.ask_regex("Set your victory message", r"^[A-Za-z0-9+/=!@#$%^&*]{1,1000}$")
                #victory_message = self.ask_regex("Set your victory message", r"^[\x00-\x7F]{1, 1000}$")
                self.save_score(file_name,passwd,victory_message,score)
                self.ask_continue()


class ForkingTCPServer(SocketServer.ForkingMixIn, SocketServer.TCPServer):
    pass

if __name__ == "__main__":
    subprocess.gc.collect()
    HOST, PORT = "0.0.0.0", 9898
    # Prevent 'cannot bind to address' errors on restart
    ForkingTCPServer.allow_reuse_address = True
    server = ForkingTCPServer((HOST, PORT), MyTCPHandler)

    ip, port = server.server_address

    if(len(sys.argv)==1):
        if(os.path.isdir(save_folder)):
            shutil.rmtree(save_folder)
        os.mkdir(save_folder)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    try:
        print "*** Power Grid service started! ***"
        server.serve_forever()
    except KeyboardInterrupt:
        print "*** Power Grid service shutting down ***"
        server.shutdown()


#FIXME check decompiled, check if comments and variable names
