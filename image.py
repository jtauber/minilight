#  MiniLight Python : minimal global illumination renderer
#
#  Copyright (c) 2007-2008, Harrison Ainsworth / HXA7241 and Juraj Sukop.
#  http://www.hxa7241.org/
#  
#  Copyright (c) 2009, James Tauber.


from math import log10
from numpy import zeros, array

PPM_ID = 'P6'
MINILIGHT_URI = 'http://www.hxa7241.org/minilight/'
DISPLAY_LUMINANCE_MAX = 200.0
RGB_LUMINANCE = array([0.2126, 0.7152, 0.0722])
GAMMA_ENCODE = 0.45


class Image(object):
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.pixels = zeros((width * height, 3))
    
    def add_to_pixel(self, x, y, radiance):
        if x >= 0 and x < self.width and y >= 0 and y < self.height:
            index = x + ((self.height - 1 - y) * self.width)
            self.pixels[index] += radiance
    
    def write_ppm(self, out, iteration):
        
        out.write('%s\n# %s\n\n%u %u\n255\n' % (PPM_ID, MINILIGHT_URI, self.width, self.height))
        
        divider = 1.0 / (max(iteration, 0) + 1)
        tonemap_scaling = calculate_tone_mapping(self.pixels, divider)
        
        for pixel in self.pixels:
            for j in range(3):
                channel = pixel[j]
                gammaed = max(channel * divider * tonemap_scaling, 0.0) ** GAMMA_ENCODE
                out.write(chr(min(int((gammaed * 255.0) + 0.5), 255)))
    
    def save(self, filename, iteration):
        f = open(filename, 'wb')
        self.write_ppm(f, iteration)
        f.close()


def calculate_tone_mapping(pixels, divider):
    sum_of_logs = 0.0
    
    for pixel in pixels:
        y = sum(divider * pixel * RGB_LUMINANCE) # pixel and RGB_LUMINANCE are vectors so this is a dot product
        sum_of_logs += log10(max(y, 0.0001))
    
    log_mean_luminance = 10.0 ** (sum_of_logs / len(pixels))
    a = 1.219 + (DISPLAY_LUMINANCE_MAX * 0.25) ** 0.4
    b = 1.219 + log_mean_luminance ** 0.4
    
    return ((a / b) ** 2.5) / DISPLAY_LUMINANCE_MAX
