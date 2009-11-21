#  MiniLight Python : minimal global illumination renderer
#
#  Copyright (c) 2007-2008, Harrison Ainsworth / HXA7241 and Juraj Sukop.
#  http://www.hxa7241.org/
#  
#  Copyright (c) 2009, James Tauber.


from math import log10


PPM_ID = 'P6'
MINILIGHT_URI = 'http://www.hxa7241.org/minilight/'
DISPLAY_LUMINANCE_MAX = 200.0
RGB_LUMINANCE = (0.2126, 0.7152, 0.0722)
GAMMA_ENCODE = 0.45


class Image(object):
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.pixels = [0.0] * width * height * 3
    
    def add_to_pixel(self, x, y, radiance):
        if x >= 0 and x < self.width and y >= 0 and y < self.height:
            index = (x + ((self.height - 1 - y) * self.width)) * 3
            self.pixels[index + 0] += radiance[0]
            self.pixels[index + 1] += radiance[1]
            self.pixels[index + 2] += radiance[2]
    
    def get_formatted(self, out, iteration):
        divider = 1.0 / (max(iteration, 0) + 1)
        tonemap_scaling = self.calculate_tone_mapping(self.pixels, divider)
        out.write('%s\n# %s\n\n%u %u\n255\n' % (PPM_ID, MINILIGHT_URI, self.width, self.height))
        
        for i in range(0, len(self.pixels), 3):
            for j in range(3):
                channel = self.pixels[i+j]
                mapped = channel * divider * tonemap_scaling
                gammaed = (mapped if mapped > 0.0 else 0.0) ** GAMMA_ENCODE
                out.write(chr(min(int((gammaed * 255.0) + 0.5), 255)))
    
    def calculate_tone_mapping(self, pixels, divider):
        sum_of_logs = 0.0
        
        for i in range(0, len(pixels), 3):
            p = pixels[i:i+3]
            y = sum(divider * j * k for j, k in zip(p, RGB_LUMINANCE))
            sum_of_logs += log10(y if y > 1e-4 else 1e-4)
        
        log_mean_luminance = 10.0 ** (sum_of_logs / (len(pixels) / 3))
        a = 1.219 + (DISPLAY_LUMINANCE_MAX * 0.25) ** 0.4
        b = 1.219 + log_mean_luminance ** 0.4
        
        return ((a / b) ** 2.5) / DISPLAY_LUMINANCE_MAX
    
    def save(self, filename, iteration):
        f = open(filename, 'wb')
        self.get_formatted(f, iteration)
        f.close()
