#  MiniLight Python : minimal global illumination renderer
#
#  Copyright (c) 2007-2008, Harrison Ainsworth / HXA7241 and Juraj Sukop.
#  http://www.hxa7241.org/
#  
#  Copyright (c) 2009, James Tauber.


from numpy import array

from math import pi, tan
from random import random
from raytracer import RayTracer
from vector3f import Vector3f

MIN_ANGLE = 10.0
MAX_ANGLE = 160.0


class Camera(object):
    
    # view_position
    # view_direction
    # view_angle (radians)
    # right
    # up
    
    def __init__(self, position, direction, angle):
        
        self.view_position = Vector3f(position)
        self.view_direction = Vector3f(direction).unitize()
        
        if self.view_direction.is_zero():
            self.view_direction = Vector3f(0.0, 0.0, 1.0)
        
        self.view_angle = min(max(MIN_ANGLE, float(angle)), MAX_ANGLE) * (pi / 180.0)
        
        # calculate right and up
        
        self.right = Vector3f(0.0, 1.0, 0.0).cross(self.view_direction).unitize()
        
        if self.right.is_zero():
            self.up = Vector3f(0.0, 0.0, 1.0 if self.view_direction.y else -1.0)
            self.right = self.up.cross(self.view_direction).unitize()
        else:
            self.up = self.view_direction.cross(self.right).unitize()
    
    
    def get_frame(self, scene, image):
        
        raytracer = RayTracer(scene)
        aspect = float(image.height) / float(image.width)
        
        for y in range(image.height):
            for x in range(image.width):
                
                ## convert x, y into sample_direction
                
                x_coefficient = ((x + random()) * 2.0 / image.width) - 1.0
                y_coefficient = ((y + random()) * 2.0 / image.height) - 1.0
                
                offset = self.right * x_coefficient + self.up * (y_coefficient * aspect)
                sample_direction = (self.view_direction + (offset * tan(self.view_angle * 0.5))).unitize()
                
                # calculate radiance from that direction
                
                radiance = array(list(raytracer.get_radiance(self.view_position, sample_direction)))
                
                # and add to image
                
                image.add_radiance(x, y, radiance)
