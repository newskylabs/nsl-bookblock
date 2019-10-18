"""newskylabs/tools/bookblock/logic/page.py:
   
Page.

"""

__author__      = "Dietrich Bollmann"
__email__       = "dietrich@formgames.org"
__copyright__   = "Copyright 2019 Dietrich Bollmann"
__license__     = "Apache License 2.0, http://www.apache.org/licenses/LICENSE-2.0"
__date__        = "2019/10/18"

import sys, re

from pathlib import Path, PosixPath

from kivy.logger import Logger

# Numpy
import numpy as np

# OpenCV
import cv2

## =========================================================
## parse_geometry(geometry)
## ---------------------------------------------------------

# Example: 600x800+22+41
g_regexp_geometry = re.compile('(\d+)x(\d+)\+(\d+)\+(\d+)')

def parse_geometry(geometry):
    """
    Example: 600x800+22+41
    """

    m = g_regexp_geometry.match(geometry)

    if m:
            
        width       = int(m.group(1))
        height      = int(m.group(2))
        offset_left = int(m.group(3))
        offset_top  = int(m.group(4))

        return (width, height, offset_left, offset_top)

    else:
        Logger.debug("parse_geometry(): From page {} to page {} left side {} right side {}"\
              .format(from_page, to_page, left_side, right_side))
            
        print("ERROR Malformed geometry: '{}'".format(geometry), file=sys.stderr)
        exit(-1)

## =========================================================
## class Page:
## ---------------------------------------------------------

class Page:
    """
    """

    def __init__(self, settings):
        self._settings = settings

    def get(self, page_spec):

        # Get the view mode
        view_mode = self._settings.get_view_mode()
        Logger.debug("Page: View mode: {}".format(view_mode))

        # Depending on the view mode return one of:
        # - scan with bounding boxraw scan
        # - page corresponding to the bounding box
        # - scan as it is
        if view_mode == 'scan':
            page = self.get_scan_with_bounding_box(page_spec)
            Logger.debug("Page: scan type(page): {}".format(type(page)))

        elif view_mode == 'page':
            page = self.get_page(page_spec)
            Logger.debug("Page: page type(page): {}".format(type(page)))

        else: # view_mode == 'raw':
            page = self.get_scan_raw(page_spec)
            Logger.debug("Page: raw type(page): {}".format(type(page)))

        Logger.debug("Pages: type(page): {}".format(type(page)))
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
        msg = \
            "DEBUG [Page] Loading Scanned page:\n" + \
            "\n" + \
            "  - scan:               {}\n".format(scan) + \
            "  - image_mode:         {}\n".format(image_mode) + \
            "  - source file:        {}\n".format(scan_path) + \
            "\n"
        Logger.debug(msg)
      
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
        msg = \
            "DEBUG [Page] Calculating bounding box:\n" + \
            "\n" + \
            "  - scan size: {}\n".format(scan_size) + \
            "  - side:      {}\n".format(side) + \
            "  - geometry:  {}\n".format(geometry) + \
            "\n"
        Logger.debug(msg)

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
        msg = \
            "DEBUG [Page] Draw bounding box on scanned page:\n" + \
            "\n" + \
            "  - scan:        {}\n".format(scan) + \
            "  - side:        {}\n".format(side) + \
            "  - page:        {}\n".format(page) + \
            "  - source file: {}\n".format(scan_path) + \
            "  - geometry:    {}\n".format(geometry) + \
            "\n"
        Logger.debug(msg)
      
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
        msg = \
            "DEBUG [Pages] Draw bounding box on scanned page:\n" + \
            "\n" + \
            "  - scan:        {}\n".format(scan) + \
            "  - side:        {}\n".format(side) + \
            "  - page:        {}\n".format(page) + \
            "  - source file: {}\n".format(scan_path) + \
            "  - geometry:    {}\n".format(geometry) + \
            "\n"
        Logger.debug(msg)
            
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
        Logger.debug("Page: Cutting out area: x: {}, y: {}, w: {}, h: {}".format(x, y, w, h))
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
        msg = \
            "DEBUG [Page] Store page:\n" + \
            "\n" + \
            "  - page:        {}\n".format(page) + \
            "  - scan:        {}\n".format(scan) + \
            "  - side:        {}\n".format(side) + \
            "  - geometry:    {}\n".format(geometry) + \
            "  - target file: {}\n".format(page_path) + \
            "\n"
        Logger.debug(msg)

        page = self.get_page(page_spec)

        # When the page has not been found return False
        if not isinstance(page, (str, np.ndarray)):
            return False

        # Ensure that the page directory exists
        page_dir = PosixPath(page_path).parent
        if not page_dir.exists():
            Logger.debug("Pages: Creating page directory: {}".format(str(page_dir)))
            page_dir.mkdir(parents=True, exist_ok=True)

        # Save image
        Logger.debug("Pages: Storing image: {}".format(page_path))
        cv2.imwrite(page_path, page)

## =========================================================
## =========================================================

## fin.
