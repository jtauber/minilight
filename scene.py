#  MiniLight Python : minimal global illumination renderer
#
#  Copyright (c) 2007-2008, Harrison Ainsworth / HXA7241 and Juraj Sukop.
#  http://www.hxa7241.org/
#  
#  Copyright (c) 2009, James Tauber.


from random import choice
from triangle import Triangle
from vector3f import Vector3f, ZERO, ONE, MAX

MAX_FLOAT = float(2**1024 - 2**971)


class Scene(object):
    
    def __init__(self, sky_emission, ground_reflection, eye_position, t):
        self.sky_emission = Vector3f(sky_emission).clamped(ZERO, MAX)
        self.ground_reflection = Vector3f(ground_reflection).clamped(ZERO, ONE)
        
        self.triangles = []
        self.emitters = []
        
        for v0, v1, v2, r, e in t:
            triangle = Triangle(v0, v1, v2, r, e)
            self.triangles.append(triangle)
            if not triangle.emitivity.is_zero() and triangle.area > 0.0:
                self.emitters.append(triangle)
                
        print "loaded %d triangles (%d emitters)" % (len(self.triangles), len(self.emitters))
        
    def get_emitter(self):
        if self.emitters:
            emitter = choice(self.emitters)
            return [emitter.get_sample_point(), emitter]
        else:
            return [ZERO, None]
    
    def emitters_count(self):
        return len(self.emitters)
    
    def get_default_emission(self, back_direction):
        if back_direction.y < 0.0:
            return self.sky_emission
        else:
            return self.sky_emission * self.ground_reflection
    
    def get_intersection(self, ray_origin, ray_direction):
        hit_object = hit_position = None
        
        nearest_distance = MAX_FLOAT
        
        for triangle in self.triangles:
            distance = triangle.get_intersection(ray_origin, ray_direction)
            
            if distance and (distance < nearest_distance):
                hit_object = triangle
                hit_position = ray_origin + ray_direction * distance
                nearest_distance = distance
        
        return hit_object, hit_position
