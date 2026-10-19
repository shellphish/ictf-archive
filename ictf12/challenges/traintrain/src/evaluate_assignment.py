#!/usr/bin/env python
import sys
import logging
import optparse
import random
import networkx as nx

def equal_path(path1, path2):
    if len(path1) != len(path2):
        return False
    for i in range(len(path1)):
        if str(path1[i]) != str(path2[i]):
            return False
    return True
    
def check_solution(assignment, solution, logger):
    res = 0
    try:
        #print assignment
        lines = assignment.split('\n')
        
        nodes = eval(lines[0])
        edges = eval(lines[1])
        start = int(lines[2].strip())
        end = int(lines[3].strip())
        
        graph = nx.Graph()
        graph.add_nodes_from(nodes)
        graph.add_edges_from(edges)
        
        shortest_paths = nx.all_shortest_paths(graph, source=start, target=end)
        solution_path = list()
        for s in solution.split(','):
            solution_path.append(int(s)) 
            
        logger.debug("Solution: %s" % str(solution_path))
        
        for p in shortest_paths:
            logger.debug("Comparing %s and %s" % (str(p), str(solution_path)))
            if equal_path(p, solution_path) == True:
                res = len(solution_path)
                break
        
    except Exception, e:
        logger.error("Solution verification failed: %s" % str(e))
    return res

def main(argv):

    parser = optparse.OptionParser()
    parser.add_option("-d", "--debug",
                      dest="debug", action="store_true",
                      help="enables debugging",
                      default="False")
    parser.add_option("-i", "--input",
                      dest="filename", type="string",
                      help="specifies the input file",
                      default="assignment")
    parser.add_option("-s", "--solution",
                      dest="solution", type="string",
                      help="specifies the solution",
                      default=None)
    
    (cmdline_options, args) = parser.parse_args()
    if len(args) != 0:
        parser.print_help()
        return 0

    if cmdline_options.debug == True:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    logger = logging.getLogger('Evaluate assignment')

    logger.debug("Starting...")
    solution = cmdline_options.solution
    
    if solution == None:
        logger.error("Missing solution")
        return 0
    infile = open(cmdline_options.filename, "r")
    assignment = infile.read()
    infile.close()
    res = check_solution(assignment, solution, logger)    
    
    logger.debug("...Finished. Returning %d" % res)
    return res

if __name__== "__main__":
    sys.exit(main(sys.argv))
