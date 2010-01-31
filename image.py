#  MiniLight Python : minimal global illumination renderer
#
#  Copyright (c) 2007-2008, Harrison Ainsworth / HXA7241 and Juraj Sukop.
#  http://www.hxa7241.org/
#  
#  Copyright (c) 2009-2010, James Tauber.


from math import log10
from numpy import zeros, array

PPM_ID = "P6"
MINILIGHT_URI = "http://www.hxa7241.org/minilight/"

# how much each channel contributes to luminance
RGB_LUMINANCE = array([0.2126, 0.7152, 0.0722])

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
        self.pixels = zeros((width * height, 3))
    
    def add_radiance(self, x, y, radiance):
        """
        add radiance (an RGB numpy array) to given x, y position on image.
        """
        if x >= 0 and x < self.width and y >= 0 and y < self.height:
            index = x + ((self.height - 1 - y) * self.width)
            self.pixels[index] += radiance
    
    def display_pixels(self, iterations):
        """
        iterate over each channel of each pixel in image returning
        gamma-corrected number scaled 0 - 1 (although not clipped to 1).
        """
        scalefactor = calculate_scalefactor(self.pixels, iterations)
        
        for pixel in self.pixels:
            for channel in pixel:
                yield max(channel * scalefactor / iterations, 0) ** GAMMA_ENCODE
    
    def save(self, filename, iterations):
        """
        save the image to given filename assuming the given number
        of iterations.
        """
        
        f = open(filename, "wb")
        f.write("%s\n# %s\n\n%u %u\n255\n" % (
            PPM_ID, MINILIGHT_URI, self.width, self.height))
        
        for c in self.display_pixels(iterations):
            f.write(chr(min(int((c * 255.0) + 0.5), 255)))
        f.close()


def calculate_scalefactor(pixels, iterations):
    """
    calculate the linear tone-mapping scalefactor for the given array
    of pixels assuming the given number of iterations.
    """
    ## calculate the log-mean luminance of the image
    
    sum_of_logs = 0.0
    
    for pixel in pixels:
        # pixel and RGB_LUMINANCE are vectors so this is a dot product
        y = sum(pixel * RGB_LUMINANCE / iterations)
        sum_of_logs += log10(max(y, 0.0001))
    
    log_mean_luminance = 10.0 ** (sum_of_logs / len(pixels))
    
    ## calculate the scalefactor for linear tone-mapping
    
    # formula from Ward "A Contrast-Based Scalefactor for Luminance Display"
    
    scalefactor = (
        (SCALEFACTOR_NUMERATOR / (1.219 + log_mean_luminance ** 0.4)) ** 2.5
    ) / DISPLAY_LUMINANCE_MAX
    
    return scalefactor
