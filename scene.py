#  MiniLight Python : minimal global illumination renderer
#
#  Copyright (c) 2007-2008, Harrison Ainsworth / HXA7241 and Juraj Sukop.
#  http://www.hxa7241.org/
#
#  Copyright (c) 2009-2012, James Tauber.


from random import choice

from spatialindex import NullSpatialIndex
from triangle import Triangle
from vector3f import Vector3f, ZERO, ONE, MAX


class Scene(object):

    def __init__(self, sky_emission, ground_reflection, eye_position, t):
        self.sky_emission = Vector3f(sky_emission).clamped(ZERO, MAX)
        self.ground_reflection = Vector3f(ground_reflection).clamped(ZERO, ONE)

        triangles = []
        self.emitters = []

        for v0, v1, v2, r, e in t:
            triangle = Triangle(v0, v1, v2, r, e)
            triangles.append(triangle)
            if not triangle.emitivity.is_zero() and triangle.area > 0.0:
                self.emitters.append(triangle)

        print "loaded %d triangles (%d emitters)" % (
            len(triangles), len(self.emitters))

        self.index = NullSpatialIndex(eye_position, triangles)
        print "built spatial index (%d deep)" % self.index.deepest_level
        self.get_intersection = self.index.get_intersection

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
