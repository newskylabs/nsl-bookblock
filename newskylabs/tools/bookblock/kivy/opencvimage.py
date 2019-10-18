"""newskylabs/tools/bookblock/kivy/opencvimage.py:
   
class OpenCVImage.

"""

__author__      = "Dietrich Bollmann"
__email__       = "dietrich@formgames.org"
__copyright__   = "Copyright 2019 Dietrich Bollmann"
__license__     = "Apache License 2.0, http://www.apache.org/licenses/LICENSE-2.0"
__date__        = "2019/10/18"

# Numpy
import numpy as np

# OpenCV
import cv2

from kivy.uix.image import Image
from kivy.graphics.texture import Texture

## =========================================================
## class OpenCVImage()
## 
## A kivy widget to display OpenCV images.
## ---------------------------------------------------------

class OpenCVImage(Image):
    """
    A kivy widget to display OpenCV images.
    """

    def populate_texture(self, texture):
        """
        Blit the image buffer.
        """
        texture.blit_buffer(self._cbuffer, colorfmt='bgr', bufferfmt='ubyte')

    def set_image(self, image, image_mode=None):
        """
        IMAGE can either be a string encoding an image file path - 
        or a numpy.ndarray encoding an image.

        In the first case the image can be loaded either as
        grayscale image when using image_mode=cv2.IMREAD_GRAYSCALE,
        or as a coloure image when using image_mode=cv2.IMREAD_COLOR.
        """

        # Ensure that IMAGE is neither an image path 
        # or a numpy.ndarray encoding an image
        if isinstance(image, str):
            # An image path has been given - load the image

            # When no image_mode has been given
            # use cv2.IMREAD_COLOR as default image mode
            if image_mode == None:
                image_mode = cv2.IMREAD_COLOR
                
            # Load the image from the given image file
            image = cv2.imread(image, image_mode)
            
        elif isinstance(image, np.ndarray):
            # An image encoded as numpy.ndarray has been given - do nothing
            pass

        else:
            # IMAGE is neither an image path 
            # nor a numpy.ndarray encoding an image
            # - raise an error
            raise TypeError("Wrong image type: {} "
                            "Only strings containing an image path "
                            "and numpy ndarrays encoding an image "
                            "are allowed as parameter of set_image()!"\
                            .format(type(image))
            )
                        
        # Kivy only has colore textures:
        # Convert Grayscale images to color
        # and leave Color images as they are
        # Color or Grayscale image?
        # cv2.IMREAD_GRAYSCALE => ex shape = (600, 800)    => len(shape) = 2
        # cv2.IMREAD_COLOR     => ex shape = (600, 800, 3) => len(shape) = 3
        if len(image.shape) == 2:
            # Convert Grayscale image to RGB
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

        # Get size of image
        width, height = image.shape[:2]

        # Flip image vertically
        # (Switch between top-left and bottom-left image origin)
        image = cv2.flip(image, 0)

        # Flatten the image array 
        # into a one dimensional array
        image = image.flatten()
        
        # Convert the image array to Python bytes 
        # containing the raw data bytes in the array
        image = image.tostring()

        # Store a handle to the image buffer 
        # to make it accessible from the redraw handler
        self._cbuffer = image

        # Create a BGR texture of the given height
        # (OpenCV uses BGR color format: BGR was more popular among camera
        # manufacturers then RGB when OpenCV was created...)
        texture = Texture.create(size=(height, width), colorfmt='bgr', bufferfmt='ubyte')
        
        # Add a handler to reload the texture 
        # when the image widget has been resized
        texture.add_reload_observer(self.populate_texture)

        # Now blit the texture buffer
        self.populate_texture(texture)

        # Display the texture
        # in the image widget
        self.texture = texture

## =========================================================
## =========================================================

## fin.
