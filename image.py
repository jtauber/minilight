#  MiniLight Python : minimal global illumination renderer
#
#  Copyright (c) 2007-2008, Harrison Ainsworth / HXA7241 and Juraj Sukop.
#  http://www.hxa7241.org/
#  
#  Copyright (c) 2009-2011, James Tauber.


from array import array
from math import log10


PPM_ID = "P6"
MINILIGHT_URI = "http://www.hxa7241.org/minilight/"

# how much each channel contributes to luminance
RGB_LUMINANCE = (0.2126, 0.7152, 0.0722)

DISPLAY_LUMINANCE_MAX = 200.0

# formula from Ward "A Contrast-Based Scalefactor for Luminance Display"
SCALEFACTOR_NUMERATOR = 1.219 + (DISPLAY_LUMINANCE_MAX * 0.25) ** 0.4


GAMMA_ENCODE = 0.45


class Image(object):
    
    def __init__(self, width, height):
        """
        initialize blank image.
        """
        self.width = width
        self.height = height
        self.data = array("d", [0]) * (width * height * 3)
    
    def _index(self, t):
        x, y, channel = t
        index = (x + ((self.height - 1 - y) * self.width)) * 3 + channel
        
        return min(max(index, 0), len(self.data) - 1)
    
    def __getitem__(self, t):
        return self.data[self._index(t)]
    
    def __setitem__(self, t, val):
        self.data[self._index(t)] = val
    
    def add_radiance(self, x, y, radiance):
        """
        add radiance (an RGB tuple) to given x, y position on image.
        """
        self[x, y, 0] += radiance[0]
        self[x, y, 1] += radiance[1]
        self[x, y, 2] += radiance[2]
    
    def calculate_scalefactor(self, iterations):
        """
        calculate the linear tone-mapping scalefactor for this image assuming
        the given number of iterations.
        """
        ## calculate the log-mean luminance of the image
        
        sum_of_logs = 0.0
        
        for x in range(self.width):
            for y in range(self.height):
                lum = self[x, y, 0] * RGB_LUMINANCE[0]
                lum += self[x, y, 1] * RGB_LUMINANCE[1]
                lum += self[x, y, 2] * RGB_LUMINANCE[2]
                lum /= iterations
                
                sum_of_logs += log10(max(lum, 0.0001))
                
        log_mean_luminance = 10.0 ** (sum_of_logs / (self.height * self.width))
        
        ## calculate the scalefactor for linear tone-mapping
        
        # formula from Ward "A Contrast-Based Scalefactor for Luminance Display"
        
        scalefactor = (
            (SCALEFACTOR_NUMERATOR / (1.219 + log_mean_luminance ** 0.4)) ** 2.5
        ) / DISPLAY_LUMINANCE_MAX
        
        return scalefactor
    
    def display_pixels(self, iterations):
        """
        iterate over each channel of each pixel in image returning
        gamma-corrected number scaled 0 - 1 (although not clipped to 1).
        """
        scalefactor = self.calculate_scalefactor(iterations)
        
        for value in self.data:
            yield max(value * scalefactor / iterations, 0) ** GAMMA_ENCODE
    
    def save(self, filename, iterations):
        """
        save the image to given filename assuming the given number
        of iterations.
        """
        
        with open(filename, "wb") as f:
            f.write("%s\n# %s\n\n%u %u\n255\n" % (
                PPM_ID, MINILIGHT_URI, self.width, self.height))
            
            for c in self.display_pixels(iterations):
                f.write(chr(min(int((c * 255.0) + 0.5), 255)))
