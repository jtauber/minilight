#  MiniLight Python : minimal global illumination renderer
#
#  Copyright (c) 2007-2008, Harrison Ainsworth / HXA7241 and Juraj Sukop.
#  http://www.hxa7241.org/
#  
#  Copyright (c) 2009, James Tauber.


import re

def parse_image_dimensions(in_stream):
    for line in in_stream:
        if not line.isspace():
            width, height = map(lambda dimension: min(max(1, int(dimension)), 10000), line.split())
            break
    return width, height


CAMERA = re.compile('(\(.+\))\s*(\(.+\))\s*(\S+)')

def parse_camera_description(in_stream):
    for line in in_stream:
        if not line.isspace():
            position, direction, angle = CAMERA.search(line).groups()
            break
    return position, direction, angle

def parse_iterations(in_stream):
    for line in in_stream:
        if not line.isspace():
            iterations = int(line)
            break
    return iterations

SKY_GROUND = re.compile('(\(.+\))\s*(\(.+\))')

def parse_sky_ground(in_stream):
    for line in in_stream:
        if not line.isspace():
            sky_emission, ground_reflection = SKY_GROUND.search(line).groups()
            break
    return sky_emission, ground_reflection


TRIANGLE = re.compile('(\(.+\))\s*(\(.+\))\s*(\(.+\))\s*(\(.+\))\s*(\(.+\))')

def parse_triangles(in_stream):
    for line in in_stream:
        if not line.isspace():
            v0, v1, v2, r, e = TRIANGLE.search(line).groups()
            yield v0, v1, v2, r, e
    raise StopIteration
