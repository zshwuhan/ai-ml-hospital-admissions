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
import random
import sys

import matplotlib.pyplot as plot

from kgers.core import KGERSCore
from rtkgers.original import RTKGERSOriginal
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
    
    test = random.sample(points, max([int(len(points) * .3), points[0].dimension]))
    training = list(set(points).difference(set(test)))
    
    rtkgers = RTKGERSOriginal('KGERSOriginal', training)
    rtkgers.populate()
    
    point = test[0]
    print(point)
    print(rtkgers.solve(point))
    
    

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