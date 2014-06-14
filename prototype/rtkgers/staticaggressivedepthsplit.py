"""
The style guide follows the strict python PEP 8 guidelines.
@see http://www.python.org/dev/peps/pep-0008/

@author Aaron Zampaglione <azampagl@azampagl.com>
@requires Python >=2.7
@copyright 2013 - Present Aaron Zampaglione
"""
import random
import sys

from scipy import stats

from common.node import Node

from common.hyperplane_exception import HyperplaneException
from kgers.original import KGERSOriginal
from kgers.diameter import KGERSDiameter
from kgers.weights import KGERSWeights
from kgers.diameterweights import KGERSDiameterWeights

from rtkgers.core import RTKGERSCore

class RTKGERSStaticAggressiveDepthSplit(RTKGERSCore):
    """
    """
    
    #
    #
    #
    NUM_OF_VALIDATION_POINTS = 20
    
    def populate(self):
        """
        """
        
        self.root = Node()
        self.root.feature = None
        self.root.threshold = None
        self.root.hyperplane = globals()[self.algorithm](self.points)
        self.root.hyperplane.execute()
        
        self.validation = set(random.sample(self.points, int(len(self.points) * .3)))
        
        self.grow(self.root, self.points)
    
    def grow(self, node, points):
        """
        """
        node.points = points
        
        # Return if we do not have enough points to split.
        if (len(points) < self.min_points * 2 + self.NUM_OF_VALIDATION_POINTS):
            return
        
        best_index = None
        best_feature = None
        best_left = None
        best_right = None
        best_error = sys.maxint
        
        # If we do not have enough validation points, sample more out of the point set.
        test_points = set(points).intersection(self.validation)
        if len(test_points) < self.NUM_OF_VALIDATION_POINTS:
            num_of_more_needed = self.NUM_OF_VALIDATION_POINTS - len(test_points)
            additional_test_points = random.sample(set(points).difference(test_points), num_of_more_needed)
            test_points = test_points.union(set(additional_test_points))
        
        training_points = list(set(points).difference(test_points))
        test_points = list(test_points)
        
        node.hyperplane = globals()[self.algorithm](training_points)
        
        try:
            node.hyperplane.execute()
        except HyperplaneException, e:
            return
        
        original_error = node.hyperplane.error()
        ttest_pair_1 = [node.hyperplane.solve(point) for point in test_points]
        
        for f in range(len(training_points[0].features)):
            points = sorted(training_points, key=lambda x: x.features[f])
            
            i = 0
            
            last_left = None
            last_right = None
            last_error = None
            
            indicies = []
            while (len(points) > self.min_points * 2):
                half = int(len(points) / 2)
                i += half
                
                indicies.append(i)
                
                print("Splitting -\t" + self.algorithm + "\t- Feature -\t" + str(f) + "\t- Index -\t" + str(i))
                #print("Feature -\t" + str(f) + "\t- Index -\t" + str(i) + "\t- Len -\t" + str(len(points)))
                #print("Index\t\t" + str(i + node.index))
                
                left_points = points[:half]
                right_points = points[half:]
                #print("Left Size\t"  + str(len(left_points)))
                #print("Right Size\t" + str(len(right_points)))
                
                left = globals()[self.algorithm](left_points)
                right = globals()[self.algorithm](right_points)
            
                # Try to generate a hyperplane.
                try:
                    left.execute()
                    right.execute()
                except HyperplaneException, e:
                    break
                
                left_error = left.error()
                right_error = right.error()
                
                #print("LeftError\t" + str(left_error))
                #print("RightError\t" + str(right_error))
                #print("")
                
                if (right_error > left_error):
                    print("Right")
                    points = right_points
                else:
                    print("Left")
                    i -= half
                    points = left_points
            
            #
            #
            #
            
            points = sorted(training_points, key=lambda x: x.features[f])
            while len(indicies) > 0:
                i = indicies.pop()
                
                left_points = points[:i]
                right_points = points[i:]

                #print("Left Size\t"  + str(len(left_points)))
                #print("Right Size\t" + str(len(right_points)))
                
                left = globals()[self.algorithm](left_points)
                right = globals()[self.algorithm](right_points)
            
                # Try to generate a hyperplane.
                try:
                    left.execute()
                    right.execute()
                except HyperplaneException, e:
                    continue
                
                left_error = left.error()
                right_error = right.error()
                
                error = (len(left_points) / float(len(points))) * left_error + \
                        (len(right_points) / float(len(points))) * right_error
                        
                ttest_pair_2 = []
                for point in test_points:
                    if (point.features[f] <= i):
                        ttest_pair_2.append(left.solve(point))
                    else:
                        ttest_pair_2.append(right.solve(point))
                
                paired_sample = stats.ttest_rel(ttest_pair_1, ttest_pair_2)
                print(original_error)
                print(error)
                print(paired_sample)
                
                if (not (original_error < error and paired_sample[1] < 0.05)):
                    if (best_error > error):
                        best_index = i
                        best_feature = f
                        best_error = error
                        best_left = left
                        best_right = right
            
        if (best_index != None):
            #print("Splitting at " + str(best_index + node.index))
            #print("")
            node.feature = best_feature
            node.threshold = node.points[best_index].features[best_feature]
            
            
            node.left = Node()
            node.left.hyperplane = best_left
            node.left.index = best_index
            
            #print("Growing Left - " + str(len(node.points[:best_index])))
            #print("")
            self.grow(node.left, node.points[:best_index])
            
            node.right = Node()
            node.right.hyperplane = best_right
            node.right.index = best_index
            
            #print("Growing Right - " + str(len(node.points[best_index:])))
            #print("")
            self.grow(node.right, node.points[best_index:])
            
        else:
            None
            #print("")
            #print("Best error was not defeated - " + str(len(points)))