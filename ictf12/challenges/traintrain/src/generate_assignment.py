#!/usr/bin/env python
import sys
import logging
import optparse
import random
import networkx as nx
#import matplotlib.pyplot as plt

def main(argv):

    parser = optparse.OptionParser()
    parser.add_option("-d", "--debug",
                      dest="debug", action="store_true",
                      help="enables debugging",
                      default="False")
    parser.add_option("-o", "--output",
                      dest="filename", type="string",
                      help="specifies the output file",
                      default="assignment")

    (cmdline_options, args) = parser.parse_args()
    if len(args) != 0:
        parser.print_help()
        return 1

    if cmdline_options.debug == True:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    logger = logging.getLogger('Generate assignment')
    logger.debug("Starting...")
    
    try:
        file = open(cmdline_options.filename, "w+")
        
        # Size of the graph
        min_size = 30
        max_size = 60
        probability = 0.2
        links = 4
        tries = 1000
        size = random.randint(min_size, max_size)
        graph = None
        while graph == None:
            graph = nx.generators.random_graphs.connected_watts_strogatz_graph(size, links, probability, tries=tries)

        file.write("%s\n" % str(graph.nodes()))        
        print graph.nodes()
        file.write("%s\n" % str(graph.edges()))        
        print graph.edges()
        
        while True:
            start = random.choice(graph.nodes())
            end = random.choice(graph.nodes())
            if start != end:
                break
        file.write("%s\n" % str(start))        
        print start
        file.write("%s\n" % str(end))        
        print end
        file.close()
        #nx.draw(graph)
        #plt.savefig("%s.png" % cmdline_options.filename)
        logger.debug("...Finished.")
    except Exception, e:
        logger.error("Error: %s" % str(e))
        return 1
    return 0

if __name__== "__main__":
    sys.exit(main(sys.argv))
