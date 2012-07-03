#  MiniLight Python : minimal global illumination renderer
#
#  Copyright (c) 2007-2008, Harrison Ainsworth / HXA7241 and Juraj Sukop.
#  http://www.hxa7241.org/
#
#  Copyright (c) 2009-2012, James Tauber.


from surfacepoint import SurfacePoint
from vector3f import ZERO


class RayTracer(object):
    
    def __init__(self, scene):
        
        self.scene = scene
    
    def get_radiance(self, ray_origin, ray_direction, last_hit=None):
        
        hit_object, hit_position = self.scene.get_intersection(ray_origin, ray_direction, last_hit)
        
        if hit_object:
            surface_point = SurfacePoint(hit_object, hit_position)
            
            if last_hit:
                local_emission = ZERO
            else:
                local_emission = surface_point.get_emission(ray_origin, -ray_direction, False)
            
            illumination = self.sample_emitters(ray_direction, surface_point)
            next_direction, color = surface_point.get_next_direction(-ray_direction)
            
            if next_direction.is_zero():
                reflection = ZERO
            else:
                reflection = color * self.get_radiance(surface_point.position, next_direction, surface_point.triangle)
            
            return reflection + illumination + local_emission
        else:
            return self.scene.get_default_emission(-ray_direction)
    
    def sample_emitters(self, ray_direction, surface_point):
        
        emitter_position, emitter = self.scene.get_emitter()
        
        if emitter:
            emit_direction = (emitter_position - surface_point.position).unitize()
            hit_object, hit_position = self.scene.get_intersection(surface_point.position, emit_direction, surface_point.triangle)
            
            if not hit_object or emitter == hit_object:
                emission_in = SurfacePoint(emitter, emitter_position).get_emission(surface_point.position, -emit_direction, True)
            else:
                emission_in = ZERO
            
            return surface_point.get_reflection(emit_direction, emission_in * self.scene.emitters_count(), -ray_direction)
        else:
            return ZERO
