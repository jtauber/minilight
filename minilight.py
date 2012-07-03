#  MiniLight Python : minimal global illumination renderer
#
#  Copyright (c) 2007-2008, Harrison Ainsworth / HXA7241 and Juraj Sukop.
#  http://www.hxa7241.org/
#
#  Copyright (c) 2009-2012, James Tauber.


from camera import Camera
from image import Image
from scene import Scene

from scene_parser import *

from sys import argv


MODEL_FORMAT_ID = "#MiniLight"


model_file_pathname = argv[1]
image_file_pathname = model_file_pathname + ".png"
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

for iteration in range(iterations):
    camera.get_frame(scene, image)
    print "iteration:", iteration + 1

image.save(image_file_pathname, iteration + 1)
print "\nfinished"
