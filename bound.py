from vector3f import Vector3f, MAX

class Bound(object):
    
    def __init__(self, lower, upper):
        self.lower = lower
        self.upper = upper
    
    def expand_to_fit(self, bound):
        for j in range(3):
            if self.lower[j] > bound.lower[j]:
                self.lower[j] = bound.lower[j]
            if self.upper[j] < bound.upper[j]:
                self.upper[j] = bound.upper[j]
    
    def clamp(self):
        size = max(list(Vector3f(self.upper) - Vector3f(self.lower)))
        self.upper = list(Vector3f(self.upper).clamped(Vector3f(self.lower) + Vector3f(size), MAX))
    
    def encloses(self, bound):
        return (
            bound.upper[0] >= self.lower[0] and bound.lower[0] < self.upper[0] and \
            bound.upper[1] >= self.lower[1] and bound.lower[1] < self.upper[1] and \
            bound.upper[2] >= self.lower[2] and bound.lower[2] < self.upper[2]
        )
