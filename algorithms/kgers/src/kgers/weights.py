"""
The style guide follows the strict python PEP 8 guidelines.
@see http://www.python.org/dev/peps/pep-0008/

@author Aaron Zampaglione <azampagl@azampagl.com>
@requires Python >=2.7
@copyright 2013 - Present Aaron Zampaglione
"""
from Queue import PriorityQueue

from core import KGERSCore
from .hyperplane import Hyperplane

class KGERSWeights(KGERSCore):
    
    def execute(self, k = 10):
        """
        """
        
        hyperplane_queue = PriorityQueue()
        for i in range(0, k * 2):
            # Grab a set of samples from the data set.
            samples = self.samples()
            # Grab a set of validators that are not in the sample set, and skip validation checks.
            validators = self.samples(exclude=samples, check=False)
            
            #print("Samples:" + str([str(point) for point in samples]))
            #print("Validators:" + str([str(point) for point in validators]))
            
            # Generate a hyperplane.
            hyperplane = Hyperplane(samples)
            # Generate the weight of the hyperplane.
            weight = self.weigh(hyperplane, validators)
            
            # Insert it into the queue, with the higher weights in front.
            hyperplane_queue.put((1.0 / weight, (hyperplane, weight)))
        
        # Only take the top half hyperplanes with the largest weight.
        self.hyperplanes = []
        self.weights = []
        for i in range(0, k):
            hyperplane, weight = hyperplane_queue.get()[1]
            self.hyperplanes.append(hyperplane)
            self.weights.append(weight)
        
        self.average()