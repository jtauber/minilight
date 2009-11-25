#  MiniLight Python : minimal global illumination renderer
#
#  Copyright (c) 2007-2008, Harrison Ainsworth / HXA7241 and Juraj Sukop.
#  http://www.hxa7241.org/
#  
#  Copyright (c) 2009, James Tauber.


#import psyco
#psyco.full()

from camera import Camera
from image import Image
from scene import Scene

from parser import *

from math import log10
from sys import argv, stdout

BANNER = """
  MiniLight 1.5.2 Python
  Copyright (c) 2008, Harrison Ainsworth / HXA7241 and Juraj Sukop.
  http://www.hxa7241.org/minilight/
  Copyright (c) 2009, James Tauber.
"""

HELP = """
----------------------------------------------------------------------
  MiniLight 1.5.2 Python
  
  Copyright (c) 2008, Harrison Ainsworth / HXA7241 and Juraj Sukop.
  http://www.hxa7241.org/minilight/
  Copyright (c) 2009, James Tauber.
  
  2009-11-21
----------------------------------------------------------------------

MiniLight is a minimal global illumination renderer.

usage:
  minilight image_file_pathname

The model text file format is:
  #MiniLight
  
  iterations
  
  imagewidth imageheight
  
  viewposition viewdirection viewangle
  
  skyemission groundreflection
  vertex0 vertex1 vertex2 reflectivity emitivity
  vertex0 vertex1 vertex2 reflectivity emitivity
  ...

-- where iterations and image values are ints, viewangle is a float,
and all other values are three parenthised floats. The file must end
with a newline. Eg.:
  #MiniLight

  100

  200 150

  (0 0.75 -2) (0 0 1) 45

  (3626 5572 5802) (0.1 0.09 0.07)
  (0 0 0) (0 1 0) (1 1 0)  (0.7 0.7 0.7) (0 0 0)
"""

MODEL_FORMAT_ID = "#MiniLight"


if __name__ == "__main__":
    if len(argv) < 2 or argv[1] == "-?" or argv[1] == "--help":
        print HELP
    else:
        print BANNER
        
        model_file_pathname = argv[1]
        image_file_pathname = model_file_pathname + ".ppm"
        model_file = open(model_file_pathname, "r")
        
        if model_file.next().strip() != MODEL_FORMAT_ID:
            raise "invalid model file"
        
        iterations = parse_iterations(model_file)
        
        width, height = parse_image_dimensions(model_file)
        image = Image(width, height)
        
        position, direction, angle = parse_camera_description(model_file)
        camera = Camera(position, direction, angle)
        
        sky_emission, ground_reflection = parse_sky_ground(model_file)
        triangles = parse_triangles(model_file)
        scene = Scene(sky_emission, ground_reflection, camera.view_position, triangles)
        
        model_file.close()
        
        for frame_no in range(1, iterations + 1):
            camera.get_frame(scene, image)
            stdout.write("\b" * ((int(log10(frame_no - 1)) if frame_no > 1 else -1) + 12) + "iteration: %u" % frame_no)
            stdout.flush()
        
        image.save(image_file_pathname, frame_no)
        print "\nfinished"
