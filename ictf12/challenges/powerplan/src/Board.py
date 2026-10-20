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
    
