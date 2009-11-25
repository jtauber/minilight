#  MiniLight Python : minimal global illumination renderer
#
#  Copyright (c) 2007-2008, Harrison Ainsworth / HXA7241 and Juraj Sukop.
#  http://www.hxa7241.org/
#  
#  Copyright (c) 2009, James Tauber.


from triangle import Triangle, TOLERANCE
from vector3f import Vector3f, MAX
from bound import Bound

MAX_LEVELS = 44
MAX_ITEMS  =  8

MAX_FLOAT = float(2**1024 - 2**971)

class SpatialIndex(object):

    def __init__(self, eye_position, items):
        
        bound = Bound(list(eye_position), list(eye_position))
        
        item_bounds = []
        
        for item in items:
            b = item.get_bound()
            item_bound = Bound(b[0:3], b[3:6])
            item_bounds.append((item, item_bound))
            bound.expand_to_fit(item_bound)
        
        bound.clamp()
        
        self.root = SpatialNode(bound, item_bounds, 0)
        self.deepest_level = self.root.deepest_level
    
    def get_intersection(self, ray_origin, ray_direction, last_hit):
        return self.root.get_intersection(ray_origin, ray_direction, last_hit, ray_origin)


class SpatialNode(object):
    
    # bound
    # is_branch
    # children
    # items
    
    def __init__(self, bound, item_bounds, level):
        
        self.bound = bound
        self.deepest_level = level
        
        self.is_branch = len(item_bounds) > MAX_ITEMS and level < MAX_LEVELS - 1
        
        if self.is_branch:
            q1 = 0
            self.children = [None] * 8
            
            for sub_cell in range(8):
                sub_bound = Bound([], [])
                
                for m in range(3):
                    if (sub_cell >> m) % 2 == 1:
                        sub_bound.lower.append((self.bound.lower[m] + self.bound.upper[m]) * 0.5)
                        sub_bound.upper.append(self.bound.upper[m])
                    else:
                        sub_bound.lower.append(self.bound.lower[m])
                        sub_bound.upper.append((self.bound.lower[m] + self.bound.upper[m]) * 0.5)
                
                sub_item_bounds = []
                
                for item, item_bound in item_bounds:
                    if sub_bound.encloses(item_bound):
                       sub_item_bounds.append((item, item_bound))
                
                q1 += 1 if len(sub_item_bounds) == len(item_bounds) else 0
                q2 = (sub_bound.upper[0] - sub_bound.lower[0]) < (TOLERANCE * 4.0)
                
                if len(sub_item_bounds) > 0:
                    if q1 > 1 or q2:
                        next_level = MAX_LEVELS
                    else:
                        next_level = level + 1
                    
                    self.children[sub_cell] = SpatialNode(sub_bound, sub_item_bounds, next_level)
                    if self.children[sub_cell].deepest_level > self.deepest_level:
                        self.deepest_level = self.children[sub_cell].deepest_level
            
        else:
            self.items = [item for item, item_bound in item_bounds]
    
    
    def get_intersection(self, ray_origin, ray_direction, last_hit, start):
        
        hit_object = hit_position = None
        
        if self.is_branch:
            
            if start[0] >= (self.bound.lower[0] + self.bound.upper[0]) * 0.5:
                sub_cell = 1
            else:
                sub_cell = 0
            
            if start[1] >= (self.bound.lower[1] + self.bound.upper[1]) * 0.5:
                sub_cell |= 2
            
            if start[2] >= (self.bound.lower[2] + self.bound.upper[2]) * 0.5:
                sub_cell |= 4
            
            cell_position = start
            
            while True:
                if self.children[sub_cell]:
                    hit_object, hit_position = self.children[sub_cell].get_intersection(ray_origin, ray_direction, last_hit, cell_position)
                    
                    if hit_object:
                        break
                
                step = MAX_FLOAT
                axis = 0
                
                for i in range(3):
                    if (sub_cell >> i) % 2 == 1:
                        if (ray_direction[i] < 0.0) ^ 1:
                            face = self.bound.upper[i]
                        else:
                            face = (self.bound.lower[i] + self.bound.upper[i]) * 0.5
                    else:
                        if (ray_direction[i] < 0.0) ^ 0:
                            face = self.bound.lower[i]
                        else:
                            face = (self.bound.lower[i] + self.bound.upper[i]) * 0.5
                    try:
                        distance = (face - ray_origin[i]) / ray_direction[i]
                    except:
                        distance = float(1e30000)
                    if distance <= step:
                        step = distance
                        axis = i
                
                if (((sub_cell >> axis) % 2) == 1) ^ (ray_direction[axis] < 0.0):
                    break
                
                cell_position = ray_origin + ray_direction * step
                sub_cell = sub_cell ^ (1 << axis)
        else:
            nearest_distance = MAX_FLOAT
            
            for item in self.items:
                if item != last_hit:
                    distance = item.get_intersection(ray_origin, ray_direction)
                    
                    if distance and (distance < nearest_distance):
                        hit = ray_origin + ray_direction * distance
                        
                        if self.bound.within(hit, TOLERANCE):
                           hit_object = item
                           hit_position = hit
                           nearest_distance = distance
        
        return hit_object, hit_position
