"""
The style guide follows the strict python PEP 8 guidelines.
@see http://www.python.org/dev/peps/pep-0008/

@author Aaron Zampaglione <azampagl@azampagl.com>
@requires Python >=2.4
@copyright 2013 - Present Aaron Zampaglione
"""
import csv
import getopt
import os
import sys

import matplotlib.pyplot as plot

from rtkgers.original import RTKGERSOriginal
from rtkgers.gsplit import RTKGERSGreedySplit
from rtkgers.depthgsplit import RTKGERSDepthGreedySplit
from rtkgers.staticaggressivedepthsplit import RTKGERSStaticAggressiveDepthSplit
from rtkgers.aggressivedepthsplit import RTKGERSAggressiveDepthSplit
from rtkgers.conservativedepthsplit import RTKGERSConservativeDepthSplit
from common.point import Point

def main():
    """Main execution for the feature extractor."""
    
    # Determine command line arguments.
    try:
        rawopts, _ = getopt.getopt(sys.argv[1:], 'i:')
    except getopt.GetoptError:
        usage()
        sys.exit(2)
        
    opts = {}
    
    # Process each command line argument.
    for o, a in rawopts:
        opts[o[1]] = a
    
    # The following arguments are required in all cases.
    for opt in ['i']:
        if not opt in opts:
            usage()
            sys.exit(2)
    
    # Create our reader and output files.
    reader = csv.reader(open(opts['i'], 'rb'), delimiter=',', quotechar='|') 
    
    # The points are essentially feature sets with the known solution.
    points = []
    
    # Skip the first line
    reader.next()
    for row in reader:            
        points.append(Point([float(feature) for feature in row[2:]], float(row[1])))
    
    rtkgers = RTKGERSAggressiveDepthSplit('KGERSWeights', points)
    #rtkgers = RTKGERSConservativeDepthSplit('KGERSWeights', points)
    #rtkgers = RTKGERSOriginal('KGERSWeights', points)
    rtkgers.populate()
    
    # Find the max coordinates
    max_x = max([point.coordinates[0] for point in points])
    max_y = max([point.coordinates[1] for point in points])
    min_x = min([point.coordinates[0] for point in points])
    min_y = min([point.coordinates[1] for point in points])
    plot.axis([min(min_x, 0.0) - 1, max(max_x, 10.0) + 1, min(min_y, 0.0) - 1, max(max_y, 10.0) + 1])
    
    # Draw all the points.
    figure = 1
    plot.figure(figure)
    plot.plot(
        [point.coordinates[0] for point in points],
        [point.coordinates[1] for point in points],
        'ko'
    )
    
    stack = [rtkgers.root]
    countleaves = 0
    while len(stack) > 0:
        node = stack.pop(0)
        
        if (node.left == None and node.right == None):
            start_point = Point([min([point.coordinates[0] for point in node.points])])
            end_point = Point([max([point.coordinates[0] for point in node.points])])
        
            plot.plot(
                [start_point.coordinates[0], end_point.coordinates[0]],
                [node.hyperplane.solve(start_point),node.hyperplane.solve(end_point)],
                'r-'
                )
            print(node)
            countleaves += 1
        else:
            stack.append(node.left)
            stack.append(node.right)
        #print(node)
    # Draw the graph.
    print(countleaves)
    plot.show()
    

def usage():
    """Prints the usage of the program."""
    
    print("\n" + 
          "The following are arguments required:\n" + 
          "-i: the input file containing the feature data.\n" +
          "\n" + 
          "Example Usage:\n" + 
          "python main.py -i \"features.csv\"" +
          "\n")

"""Main execution."""
if __name__ == "__main__":
    main()