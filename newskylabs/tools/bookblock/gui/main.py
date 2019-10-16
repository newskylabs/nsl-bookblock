"""newskylabs/tools/bookblock/gui/main.py:

The GUI of the nsl-bookblock tool.

"""

__author__      = "Dietrich Bollmann"
__email__       = "dietrich@formgames.org"
__copyright__   = "Copyright 2019 Dietrich Bollmann"
__license__     = "Apache License 2.0, http://www.apache.org/licenses/LICENSE-2.0"
__date__        = "2019/10/14"

#| import ...

## =========================================================
## nsl-bookblock GUI
## ---------------------------------------------------------

# General Python libs
import sys, os, re, logging
from copy import deepcopy
from pathlib import Path, PosixPath
from os.path import dirname
from time import strftime

# Numpy
import numpy as np

# OpenCV
import cv2

# Kivy
import kivy
kivy.require('1.11.1')

from kivy.app import App
from kivy.logger import Logger, LOG_LEVELS, FileHandler
from kivy.config import Config
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.graphics.texture import Texture

## =========================================================
## DEBUG
## ---------------------------------------------------------

g_settings = None

## =========================================================
## DEBUG and ERROR messages
## ---------------------------------------------------------

def debug(message):
    if g_settings and g_settings.get_debug_mode():
        print("DEBUG {}".format(message))

def error(message):
    print("ERROR {}".format(message), file=sys.stderr)
    sys.exit(-1)

def warning(message):
    print("WARNING {}".format(message), file=sys.stderr)

## =========================================================
## parse_geometry(geometry)
## ---------------------------------------------------------

# Example: 600x800+22+41
regexp_geometry = re.compile('(\d+)x(\d+)\+(\d+)\+(\d+)')

def parse_geometry(geometry):
    """
    Example: 600x800+22+41
    """

    m = regexp_geometry.match(geometry)

    if m:
            
        width       = int(m.group(1))
        height      = int(m.group(2))
        offset_left = int(m.group(3))
        offset_top  = int(m.group(4))

        return (width, height, offset_left, offset_top)

    else:
        debug("DEBUG From page {} to page {} left side {} right side {}"\
              .format(from_page, to_page, left_side, right_side))
            
        error("ERROR Malformed geometry: '{}'".format(geometry))

## =========================================================
## parse_page_spec(page_spec)
## ---------------------------------------------------------

# Example: 0l,1-3lr,4r,56l
regexp_page_spec = re.compile('(\d+)(-(\d+))?(l?)(r?)')

def parse_page_spec(page_spec):
    """
    Example: 0l,1-3lr,4r,56l
    """

    # DEBUG
    debug("page_spec: {}".format(page_spec))

    m = regexp_page_spec.match(page_spec)

    if m:
            
        from_page  = False if not m.group(1) else int(m.group(1))
        to_page    = False if not m.group(3) else int(m.group(3))
        left_side  = m.group(4) == 'l'
        right_side = m.group(5) == 'r'

        # DEBUG
        debug("From page {} to page {} left side {} right side {}"\
              .format(from_page, to_page, left_side, right_side))

        # Which scan pages should I treat?
        if to_page:
            pages = range(from_page, to_page+1)
        else:
            pages = range(from_page, from_page+1)
                
        # DEBUG
        debug("Pages: {}".format(list(pages)))

        # Which sides should I cut out?
        sides = []
        if left_side:
            sides.append('left')
        if right_side:
            sides.append('right')

        # DEBUG
        debug("Sides: {}".format(sides))

        return (pages, sides)

    else:
            
        print("ERROR Malformed page spec: '{}'".format(page_spec))
        sys.exit(2)

## =========================================================
## class Settings
## ---------------------------------------------------------

class Settings:
    """
    Settings.
    """

    def __init__(self):

        # Defaults
        self._debug              = False
        self._mode               = 'bb'
        self._image_mode         = 'color'
        self._view_mode          = 'scan'
        self._source_dir         = '/tmp'
        self._target_dir         = '/tmp'
        self._source_file_format = 'scan%03d.png'
        self._target_file_format = 'page%03d.png'
        self._geometry           = '600x800+10+20'
        self._pages              = '0l'

    def print_settings(self):

        print("")
        print("Settings:")
        print("")
        print("  - mode:               ", self._mode)
        print("  - image mode:         ", self._image_mode)
        print("  - view mode:          ", self._view_mode)        
        print("  - source_dir:         ", self._source_dir)
        print("  - target_dir:         ", self._target_dir)
        print("  - source_file_format: ", self._source_file_format)
        print("  - target_file_format: ", self._target_file_format)
        print("  - geometry:           ", self._geometry)
        print("  - pages:              ", self._pages)
        print("")

    ## Setters

    def set_debug_mode(self, debug):
        self._debug = debug

    def set_mode(self, mode):
        self._mode = mode

    def set_image_mode(self, image_mode):
        self._image_mode = image_mode

    def set_view_mode(self, view_mode):
        self._view_mode = view_mode

    def set_source_dir(self, source_dir):
        self._source_dir = source_dir

    def set_target_dir(self, target_dir):
        self._target_dir = target_dir

    def set_source_file_format(self, source_file_format):
        self._source_file_format = source_file_format

    def set_target_file_format(self, target_file_format):
        self._target_file_format = target_file_format

    def set_geometry(self, geometry):
        self._geometry = geometry

    def set_pages(self, pages):
        self._pages = pages

    ## Getters

    def get_debug_mode(self):
        return self._debug

    def get_mode(self):
        return self._mode

    def get_image_mode(self):
        return self._image_mode

    def get_view_mode(self):
        return self._view_mode

    def get_source_dir(self):
        return self._source_dir

    def get_target_dir(self):
        return self._target_dir

    def get_source_file_format(self):
        return self._source_file_format

    def get_target_file_format(self):
        return self._target_file_format

    def get_geometry(self):
        return self._geometry

    def get_pages(self):
        return self._pages

## =========================================================
## class Pages:
## ---------------------------------------------------------

class Pages:
    """
    """

    def __init__(self, settings):
        self._settings = settings
        
        # Generate the list of page specs
        self._init_page_list()

    def debug(self, message):
        if self._settings.get_debug_mode():
            print("DEBUG [Pages] {}".format(message))

    def _init_page_list(self):

        # Get the pace spec string
        # and generate a list of page specs
        # '0l,1-3lr,56l' => ['0l', '1-3lr', '56l']
        pages = self._settings.get_pages()
        page_specs = pages.split(",")
    
        page = 1
        pages = []
        for page_spec in page_specs:
            scan_pages, sides = parse_page_spec(page_spec)

            for scan in scan_pages:

                for side in sides:

                    page_spec = {
                        'scan': scan,
                        'side': side,
                        'page': page,
                    }
                    pages.append(page_spec)

                    page += 1
                
        ## DEBUG
        self.debug("pages: {}".format(pages))

        self._pages = pages
        self._num_pages = len(pages)
        self._first_page = 0
        self._last_page = self._num_pages -1
        self._current_page = 0

    def get_number_of_images(self):
        return self._num_pages

    def reset(self):
        self._current_page = 0

    def add_file_infos(self, spec):

        scan_dir = self._settings.get_source_dir()
        spec['scan-dir'] = scan_dir

        formatstr = self._settings.get_source_file_format()
        scan_file = formatstr % spec['scan']
        spec['scan-file'] = scan_file

        scan_path = str((PosixPath(scan_dir) / scan_file).expanduser())
        spec['scan-path'] = scan_path
        
        page_dir = self._settings.get_target_dir()
        spec['page-dir'] = page_dir

        formatstr = self._settings.get_target_file_format()
        page_file = formatstr % spec['page']
        spec['page-file'] = page_file

        page_path = str((PosixPath(page_dir) / page_file).expanduser())
        spec['page-path'] = page_path

    def get_pages(self):
        
        # Get the page specs of all pages
        page_specs = deepcopy(self._pages)

        # Add file infos
        for page_spec in page_specs:
            self.add_file_infos(page_spec)

        return page_specs

    def get_previous_page(self):

        if self.is_first_page():
            return None
        else:
            self._current_page -= 1
            return self.get_current_page()

    def get_current_page(self):
        spec = self._pages[self._current_page]
        self.add_file_infos(spec)
        return spec

    def get_next_page(self):

        if self.is_last_page():
            return None
        else:
            self._current_page += 1
            return self.get_current_page()

        pass

    def is_first_page(self):
        first_image_index = 0
        return self._current_page == first_image_index

    def is_last_page(self):
        last_image_index = len(self._pages) - 1
        return self._current_page == last_image_index

    def print_current_page(self):
        spec = self.get_current_page()

        if self._settings.get_debug_mode():
            print("DEBUG [Pages] Page {}:".format(spec['page']))
            print("  - scan:      {}".format(spec['scan']))
            print("  - side:      {}".format(spec['side']))
            print("  - scan-dir:  {}".format(spec['scan-dir']))
            print("  - scan-file: {}".format(spec['scan-file']))
            print("  - scan-path: {}".format(spec['scan-path']))
            print("  - page:      {}".format(spec['page']))
            print("  - page-dir:  {}".format(spec['page-dir']))
            print("  - page-file: {}".format(spec['page-file']))
            print("  - page-path: {}".format(spec['page-path']))
            print("")

        else:
            print("Showing page {}  [scan {}, {} side]"\
                  .format(spec['page'], 
                          spec['scan'],
                          spec['side']))

# TEST
#| print("")
#| print("TEST Pages:")        
#| print("")
#| 
#| settings = Settings()
#| page_spec = '0l,1-3lr,56l'
#| settings.set_pages(page_spec)
#| 
#| pages = Pages(settings)
#| print("")
#| print("page_spec:", page_spec)
#| print("pages.get_number_of_images():", pages.get_number_of_images())
#| print("")
#| print("current image:", end=' ')
#| pages.print_current_page()
#| for i in range(pages.get_number_of_images()):
#|     print("next image:", end=' ')
#|     if pages.get_next_page():
#|         pages.print_current_page()
#|     else:
#|         print("None")
#|         print("")
#| print("current image:", end=' ')
#| pages.print_current_page()
#| print("")
#| for i in range(pages.get_number_of_images()):
#|     print("previous image:", end=' ')
#|     if pages.get_previous_page():
#|         pages.print_current_page()
#|     else:
#|         print("None")
#|         print("")
#| print("current image:", end=' ')
#| pages.print_current_page()
#| 
#| exit()

## =========================================================
## class Page:
## ---------------------------------------------------------

class Page:
    """
    """

    def __init__(self, settings):
        self._settings = settings

    def debug(self, message):
        if self._settings.get_debug_mode():
            print("DEBUG [Page] {}".format(message))

    def get(self, page_spec):

        # Get the view mode
        view_mode = self._settings.get_view_mode()
        self.debug("View mode: {}".format(view_mode))

        # Depending on the view mode return one of:
        # - scan with bounding boxraw scan
        # - page corresponding to the bounding box
        # - scan as it is
        if view_mode == 'scan':
            page = self.get_scan_with_bounding_box(page_spec)
            self.debug(">>> scan type(page): {}".format(type(page)))

        elif view_mode == 'page':
            page = self.get_page(page_spec)
            self.debug(">>> page type(page): {}".format(type(page)))

        else: # view_mode == 'raw':
            page = self.get_scan_raw(page_spec)
            self.debug(">>> raw type(page): {}".format(type(page)))

        self.debug(">>> type(page): {}".format(type(page)))
        return page
        
    def get_scan_raw(self, page_spec):
        return page_spec['scan-path']

    def load_scan(self, page_spec):

        # Extract page info
        scan = page_spec['scan']

        # Define aliases for relevant settings
        image_mode = self._settings.get_image_mode()

        # Extract source and target file
        scan_path = page_spec['scan-path']

        # Print settings
        if self._settings.get_debug_mode():
            print("DEBUG [Page] Loading Scanned page:")
            print("")
            print("  - scan:               ", scan)
            print("  - image_mode:         ", image_mode)
            print("  - source file:        ", scan_path)
            print("")
      
        # Ensure that the scan file exists
        if not Path(scan_path).exists():
            # No file has been found 
            # print an ERROR and exit
            print("ERROR File not found: {}".format(scan_path), file=sys.stderr)
            sys.exit(2)

        # Select image mode
        if image_mode == 'color':
            image_mode = cv2.IMREAD_COLOR

        elif image_mode == 'grayscale':
            image_mode = cv2.IMREAD_GRAYSCALE

        else:
            # ERROR:
            # Undefined image mode
            # Only one of `color' and `grayscale' is defined.
            # - raise an error
            raise TypeError("Undefined image mode: {} "
                            "Only `color' and `grayscale' are defined."\
                            .format(type(image_mode))
            )
            
        # Load an color image in grayscale
        scan_data = cv2.imread(scan_path, image_mode)
    
        # Return the loaded scan data
        return scan_data

    def calculate_bounding_box(self, page_spec, scan_size):
        """
        Calculate the Bounding Box
        """

        # Extract page info
        side = page_spec['side']

        # Define aliases for relevant settings
        geometry = self._settings.get_geometry()

        # Print settings
        if self._settings.get_debug_mode():
            print("DEBUG [Page] Calculating bounding box:")
            print("")
            print("  - scan size: ", scan_size)
            print("  - side:      ", side)
            print("  - geometry:  ", geometry)
            print("")

        # Size of scan
        scan_height, scan_width = scan_size
        half_scan_width = int(scan_width / 2)

        # Size of page
        # parse geometry string
        bb_width, bb_height, bb_offset_left, bb_offset_top = parse_geometry(geometry)
    
        # Bounding box
        # Calculate upper left and lower right point
        # defining the bounding box
        # Default: left page
        bb_p1 = (bb_offset_left, bb_offset_top)
        bb_p2 = (bb_p1[0] + bb_width - 1, bb_p1[1] + bb_height - 1)

        # When the right page is required
        # shift the bounding box to the right page
        if side == 'right':
            bb_p1 = (half_scan_width + bb_p1[0], bb_p1[1])
            bb_p2 = (half_scan_width + bb_p2[0], bb_p2[1])
        
        # Return boundng box
        return (bb_p1, bb_p2)

    def get_scan_with_bounding_box(self, page_spec): # wech, side, mode):

        # Extract page info
        scan = page_spec['scan']
        side = page_spec['side']
        page = page_spec['page']

        # Extract source and target file
        scan_path = page_spec['scan-path']

        # Define aliases for relevant settings
        geometry           = self._settings.get_geometry()

        # Print settings
        if self._settings.get_debug_mode():
            print("DEBUG [Page] Draw bounding box on scanned page:")
            print("")
            print("  - scan:        ", scan)
            print("  - side:        ", side)
            print("  - page:        ", page)
            print("  - source file: ", scan_path)
            print("  - geometry:    ", geometry)
            print("")
      
        # Load the scan
        scan = self.load_scan(page_spec)

        # When the scan has not been found return False
        if not isinstance(scan, (str, np.ndarray)):
            return None

        # Get the size of the scan
        scan_size = scan.shape[:2]

        # Calculate the Bounding Box
        bb_p1, bb_p2 = self.calculate_bounding_box(page_spec, scan_size)

        # Bounding box settings
        bb_color      = 0 # Black
        bb_line_width = 2 # 2px line thickness

        # Draw bounding box
        cv2.rectangle(scan, bb_p1, bb_p2, bb_color, bb_line_width)

        # Return scan with bounding box
        return scan
    
    def get_page(self, page_spec):

        # Extract page info
        scan = page_spec['scan']
        side = page_spec['side']
        page = page_spec['page']

        # Extract source and target file
        scan_path = page_spec['scan-path']

        # Define aliases for relevant settings
        geometry = self._settings.get_geometry()

        # Print settings
        if self._settings.get_debug_mode():
            print("DEBUG [Pages] Draw bounding box on scanned page:")
            print("")
            print("  - scan:        ", scan)
            print("  - side:        ", side)
            print("  - page:        ", page)
            print("  - source file: ", scan_path)
            print("  - geometry:    ", geometry)
            print("")
            
        # Load the scan
        scan = self.load_scan(page_spec)

        # When the scan has not been found return False
        if not isinstance(scan, (str, np.ndarray)):
            return False

        # Get the size of the scan
        scan_size = scan.shape[:2]

        # Calculate the Bounding Box
        bb_p1, bb_p2 = self.calculate_bounding_box(page_spec, scan_size)

        # Calculate the page area
        x1, y1 = bb_p1
        x2, y2 = bb_p2
        x = x1
        y = y1
        w = x2 - x1 + 1
        h = y2 - y1 + 1
        
        # Cut out page
        self.debug("Cutting out area: x: {}, y: {}, w: {}, h: {}".format(x, y, w, h))
        page = scan.copy()
        page = page[y:y+h, x:x+w]

        # Return the page data
        return page

    def store_page(self, page_spec):

        # Extract page info
        page = page_spec['page']
        scan = page_spec['scan']
        side = page_spec['side']

        # Define aliases for relevant settings
        geometry = self._settings.get_geometry()

        # Extract source and target file
        page_path = page_spec['page-path']

        # Print settings
        if self._settings.get_debug_mode():
            print("DEBUG [Page] Store page:")
            print("")
            print("  - page:        ", page)
            print("  - scan:        ", scan)
            print("  - side:        ", side)
            print("  - geometry:    ", geometry)
            print("  - target file: ", page_path)
            print("")

        page = self.get_page(page_spec)

        # When the page has not been found return False
        if not isinstance(page, (str, np.ndarray)):
            return False

        # Ensure that the page directory exists
        page_dir = PosixPath(page_path).parent
        if not page_dir.exists():
            self.debug("Creating page directory: {}".format(str(page_dir)))
            page_dir.mkdir(parents=True, exist_ok=True)

        # Save image
        self.debug("Storing image: {}".format(page_path))
        cv2.imwrite(page_path, page)

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
## class BookBlock
## ---------------------------------------------------------

class BookBlock:
    """
    Book Block Cutter class.
    """

    def __init__(self, settings):
        self._settings = settings

        # Create the page server
        pages = Pages(settings)
        self._pages = pages

        # A service to transform a page spec
        # into an actual page
        page = Page(settings)
        self._page = page

    def debug(self, message):
        if self._settings.get_debug_mode():
            print("DEBUG [BookBlock] {}".format(message))

    def reset(self):
        self._pages.reset()

    def get_previous_page(self):

        page_spec = self._pages.get_previous_page()
        self.debug(">>> page_spec: {}".format(page_spec))
        self._pages.print_current_page()
        page = self._page.get(page_spec)
        self.debug(">>> type(page): {}".format(type(page)))
        return page

    def get_current_page(self):

        page_spec = self._pages.get_current_page()
        self.debug(">>> page_spec: {}".format(page_spec))
        self._pages.print_current_page()
        page = self._page.get(page_spec)
        self.debug(">>> type(page): {}".format(type(page)))
        return page

    def get_next_page(self):

        page_spec = self._pages.get_next_page()
        self.debug(">>> page_spec: {}".format(page_spec))
        self._pages.print_current_page()
        page = self._page.get(page_spec)
        self.debug(">>> type(page): {}".format(type(page)))
        return page

    def is_first_page(self):
        return self._pages.is_first_page()

    def is_last_page(self):
        return self._pages.is_last_page()

    def store_pages(self):

        # Get the complete list of page specs
        page_specs = self._pages.get_pages()
        for page_spec in page_specs:

            page_path = page_spec['page-path']
            print("Generating page {}".format(page_path))
            self._page.store_page(page_spec)

# TEST
#| bookblock = BookBlock()
#| print("bookblock.get_current_page():", bookblock.get_current_page())
#| print("bookblock.get_next_page():", bookblock.get_next_page())
#| print("bookblock.get_next_page():", bookblock.get_next_page())
#| print("bookblock.get_next_page():", bookblock.get_next_page())
#| print("bookblock.get_next_page():", bookblock.get_next_page())
#| print("bookblock.get_current_page():", bookblock.get_current_page())
#| print("bookblock.get_previous_page():", bookblock.get_previous_page())
#| print("bookblock.get_previous_page():", bookblock.get_previous_page())
#| print("bookblock.get_previous_page():", bookblock.get_previous_page())
#| print("bookblock.get_previous_page():", bookblock.get_previous_page())
#| print("bookblock.get_current_page():", bookblock.get_current_page())
#| exit()

## =========================================================
## GUI / App
## ---------------------------------------------------------

class BookBlockApp(App):

    def __init__(self, settings):


        
        self._settings = settings

        # Book block image server
        bookblock = BookBlock(settings)
        self._image_server = bookblock
        return super(BookBlockApp, self).__init__()
        
    def debug(self, message):
        if self._settings.get_debug_mode():
            print("DEBUG [BookBlockApp] {}".format(message))

    def get_create_config_dir(self):
        """
        Return the config dir.  If it does not exist, create it.
        """
        # Config dir 
        application_name = self.get_application_name().lower()
        config_dir_name = '~/.{}'.format(application_name)
        config_dir = Path(config_dir_name).expanduser()

        # Ensure that config directory exists
        if not config_dir.exists():
            self.debug("Creating config directlry: {}".format(config_dir_name))
            config_dir.mkdir(parents=True, exist_ok=True)

        # Return config dir
        return config_dir_name

    def get_application_config(self):
        """
        ~/.BookBlocks.ini
        """
        # Ensure that config directory exists
        config_dir = self.get_create_config_dir()

        # Config dir 
        application_config_file = '{}/config.ini'.format(str(config_dir))

        return super(BookBlockApp, self)\
            .get_application_config(application_config_file)

    def build_config(self, config):

        application_name = self.get_application_name().lower()
        application_name_lower = application_name.lower()

        # Ensure that config directory exists
        config_dir = self.get_create_config_dir()
        log_dir = '{}/{}'.format(config_dir, 'logs')
        log_file_name = '{}_log_%y-%m-%d_%_.txt'.format(application_name_lower)
        
        config.setdefaults('logger', {
            'log_level':    'warning',
            'log_enable':   1,
            'log_dir':      log_dir,
            'log_name':     log_file_name,
            #| 'log_maxfiles': 10,
        })

        config.setdefaults('gui', {
            'width': 1200,
            'height': 800
        })

    def init_logger(self):

        # Store log messages until logger is configured
        log_messages = []

        # Init log level from ~/.bookblock or the defaults
        config = self.config
        log_dir    = config.get('logger', 'log_dir')
        log_name   = config.get('logger', 'log_name')
        log_level  = LOG_LEVELS.get(config.get('logger', 'log_level'))
        log_enable = config.getint('logger', 'log_enable')
        #| log_maxfiles = config.getint('logger', 'log_maxfiles')

        # Ensure that log directory exists
        log_dir_path = PosixPath(log_dir).expanduser()
        print("log_dir_path:", log_dir_path)
        if not Path(log_dir_path).exists():
            log_messages.append("Creating log directory: {}".format(log_dir))
            log_dir_path.mkdir(parents=True, exist_ok=True)

        # Substitute the log file name format patterns with actual values
        # %y -> year, %m -> month, %d -> day, %_ -> next log file number
        log_file = log_name.replace('%_', '@@NUMBER@@')
        log_file = strftime(log_file)
        log_file = '{}/{}'.format(str(log_dir_path), log_file)
        n = 0
        while True:
            log_file2 = log_file.replace('@@NUMBER@@', str(n))
            if not os.path.exists(log_file2):
                log_file = log_file2
                break
            n += 1
            if n > 10000:  # prevent maybe flooding ?
                raise Exception('Too many logfile, remove them')
            
        # Open log file
        # and substitue it for the kivy log file (~/kivy/logs/...
        FileHandler.filename = str(log_file)
        if FileHandler.fd is not None:
            FileHandler.fd.close()
        FileHandler.fd = open(log_file, 'w')
        log_messages.append('Logger: Record log in %s' % log_file)

        # Set log level
        Logger.setLevel(log_level)

        # En- / Disable logger
        Logger.logfile_activated = bool(log_enable)

        # TODO Purge old logs
        # See site-packages/kivy/logger.py, class FileHandler, method purge_logs() 
        # for an example of how to purge old logs.

        # Log stored log messages
        for msg in log_messages:
            Logger.info(msg)
            
        # Log some general information about Python, Kivy etc.
        
        # Kivys default logging level is info
        # In order to suppress the initial INFO messages printed when kivy is loaded
        # until the log level for `bookblock' is set
        # I set the level to WARNING by in file ~/.kivy/config.ini
        # > [kivy]
        # > #log_level = info
        # > log_level = warning
        # Some of the suppressed information is printed now
        # when the bookblock log level is lower or equal to INFO

        Logger.info('Kivy: v%s' % kivy.__version__)
        Logger.info('Kivy: Installed at "{}"'.format(kivy.__file__))
        Logger.info('Python: v{}'.format(sys.version))
        Logger.info('Python: Interpreter at "{}"'.format(sys.executable))
        Logger.info('Bookblock: Installed at "{}"'.format(dirname(dirname(__file__))))
        Logger.info('Bookblock: To avoid the Kivy startup INFO messages '
                    'change the kivy log level to WARNING '
                    'in ~/.kivy/config.ini')
        Logger.info('Bookblock: To avoid further messages from Bookblock '
                    'adapt the Bookblock log level in '
                    'in ~/.bookblock')
        Logger.info('Bookblock: For more debug information '
                    'change the kivy log level in ~/.kivy/config.ini '
                    'and the Bookblock log level in ~/.bookblock/config.ini '
                    'to TRACE, DEBUG, or INFO.')

        # Example log messages
        # Log levels: trace, debug, info, warning, error, critical
        #| Logger.trace('Title: This is a trace message.')
        #| Logger.debug('Title: This is a debug message.')
        #| Logger.info('Title: This is an info message.')
        #| Logger.warning('Title: This is a warning message.')
        #| Logger.error('Title: This is an error message.')
        #| Logger.critical('Title: This is a critical message.')
    
    def build(self):

        # Init the logger
        self.init_logger()

        # Set initial window size
        config = self.config
        Config.set('graphics', 'width',  config.getint('gui', 'width'))
        Config.set('graphics', 'height', config.getint('gui', 'height'))

        # Build the GUI
        return self.build_GUI()

    def build_GUI(self):

        # ======================================
        # GUI Layout:
        # --------------------------------------
        # 
        #   +-------------------+
        #   |                   |  
        #   |                   |  
        #   |       Image       |  
        #   |                   |  
        #   |                   |  
        #   +---+---+---+---+---+
        #   | < | > | m | a | c |
        #   +---+---+---+---+---+
        # 
        #   < = previous image
        #   > = previous image
        #   m = mode: toggle view mode:
        #     - scan with bounding box
        #     - resulting page
        #   a = apply
        #   c = cancel and exit
        # 
        # --------------------------------------
        
        # Image Viewer
        image_viewer_layout = self.build_image_viewer()
        image_viewer_layout.size_hint = (1.0, 0.9)

        # Buttons
        button_layout = self.build_buttons()
        button_layout.size_hint = (1.0, 0.1)

        # Assemble the GUI
        gui_layout = BoxLayout(orientation='vertical', size=(800, 200), padding=4, spacing=4)
        gui_layout.add_widget(image_viewer_layout)
        gui_layout.add_widget(button_layout)

        # Load the first image
        self._image_server.reset()
        self.redraw_image()

        # Return the GUI
        return gui_layout

    def build_image_viewer(self):

        # Using OpenCVImage
        # which allows to show OpenCV images in a Kivy GUI
        image = OpenCVImage()

        # Assemble Image Viewer layout
        image_viewer_layout = BoxLayout(orientation='horizontal', padding=0, spacing=0)
        image_viewer_layout.add_widget(image)
        self._image_viewer = image

        # Return the image viewer layout
        return image_viewer_layout

    def build_buttons(self):

        # Previous Image Button
        previous_button = Button(text='Previous Image')
        previous_button.bind(on_press=self.previous_image)
        self._previous_button = previous_button

        # Next Image Button
        next_button = ToggleButton(text='Next Image')
        next_button.bind(on_press=self.next_image)
        self._next_button = next_button

        # Toggle View Mode Button
        toogle_view_mode_button = ToggleButton(text='Scan Mode')
        toogle_view_mode_button.bind(on_press=self.toggle_view_mode)

        # Apply Button
        apply_button = Button(text='Apply')
        apply_button.bind(on_press=self.apply)

        # Exit Button
        exit_button = Button(text='Exit')
        exit_button.bind(on_press=self.stop)

        # Arrange then in a layout group
        button_layout = BoxLayout(orientation='horizontal', padding=0, spacing=1)
        button_layout.add_widget(previous_button)
        button_layout.add_widget(next_button)
        button_layout.add_widget(toogle_view_mode_button)
        button_layout.add_widget(apply_button)
        button_layout.add_widget(exit_button)

        # Return the button layout
        return button_layout

    def redraw_image(self):
        img_path = self._image_server.get_current_page()

        # Do nothing - when the current page has not been found
        if not isinstance(img_path, (str, np.ndarray)):
            return None
        
        self.update_button_states()
        self._image_viewer.set_image(img_path)

    def show_image(self, image):

        # When no file has been found do nothing
        if not isinstance(image, (str, np.ndarray)):
            return None

        self._image_viewer.set_image(image)

    def update_button_states(self):

        first_image = self._image_server.is_first_page()
        last_image  = self._image_server.is_last_page()

        if first_image and last_image:
            # There is only one image
            self._previous_button.disabled = True
            self._next_button.disabled = True

        elif first_image:
            self._previous_button.disabled = True
            self._next_button.disabled = False

        elif last_image:
            self._previous_button.disabled = False
            self._next_button.disabled = True

        else:
            self._previous_button.disabled = False
            self._next_button.disabled = False

    def previous_image(self, instance):
        self.debug('The button <%s> has been pressed' % instance.text)

        img_file = self._image_server.get_previous_page()
        self.show_image(img_file)
        self.update_button_states()

    def next_image(self, instance):
        self.debug('The button <%s> has been pressed' % instance.text)

        img_file = self._image_server.get_next_page()
        self.show_image(img_file)
        self.update_button_states()

    def toggle_view_mode(self, instance):
        
        if instance.state == 'normal':
            print("Switched view mode to 'scan'")

            # Change button label
            instance.text = 'Scan Mode'

            self._settings.set_view_mode('scan')

        else: # instance.state == 'down'
            print("Switched view mode to 'page'")

            # Change button label
            instance.text = 'Page Mode'

            self._settings.set_view_mode('page')

        # Redraw the image
        # in the current view mode
        self.redraw_image()

    def apply(self, instance):
        self.debug('The button <%s> has been pressed' % instance.text)

        print("Generating pages:")
        self._image_server.store_pages()
        print("Done.")

## =========================================================
## =========================================================

## fin.
