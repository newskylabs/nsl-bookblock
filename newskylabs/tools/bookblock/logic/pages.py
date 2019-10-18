"""newskylabs/tools/bookblock/logic/pages.py:
   
Pages.

"""

__author__      = "Dietrich Bollmann"
__email__       = "dietrich@formgames.org"
__copyright__   = "Copyright 2019 Dietrich Bollmann"
__license__     = "Apache License 2.0, http://www.apache.org/licenses/LICENSE-2.0"
__date__        = "2019/10/18"

import re
from pathlib import PosixPath
from copy import deepcopy

from kivy.logger import Logger

## =========================================================
## parse_page_spec(page_spec)
## ---------------------------------------------------------

# Example: 0l,1-3lr,4r,56l
g_regexp_page_spec = re.compile('(\d+)(-(\d+))?(l?)(r?)')

def parse_page_spec(page_spec):
    """
    Example: 0l,1-3lr,4r,56l
    """

    # DEBUG
    Logger.debug("parse_page_spec(): page_spec: {}".format(page_spec))

    m = g_regexp_page_spec.match(page_spec)

    if m:
            
        from_page  = False if not m.group(1) else int(m.group(1))
        to_page    = False if not m.group(3) else int(m.group(3))
        left_side  = m.group(4) == 'l'
        right_side = m.group(5) == 'r'

        # DEBUG
        Logger.debug("parse_page_spec(): From page {} to page {} left side {} right side {}"\
                     .format(from_page, to_page, left_side, right_side))

        # Which scan pages should I treat?
        if to_page:
            pages = range(from_page, to_page+1)
        else:
            pages = range(from_page, from_page+1)
                
        # DEBUG
        Logger.debug("parse_page_spec(): Pages: {}".format(list(pages)))

        # Which sides should I cut out?
        sides = []
        if left_side:
            sides.append('left')
        if right_side:
            sides.append('right')

        # DEBUG
        Logger.debug("parse_page_spec(): Sides: {}".format(sides))

        return (pages, sides)

    else:
            
        print("ERROR Malformed page spec: '{}'".format(page_spec), file=sys.stderr)
        sys.exit(2)

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
        Logger.debug("Pages:pages: {}".format(pages))

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

        msg = \
            "Pages: Page {}:\n".format(spec['page']) + \
            "  - scan:      {}\n".format(spec['scan']) + \
            "  - side:      {}\n".format(spec['side']) + \
            "  - scan-dir:  {}\n".format(spec['scan-dir']) + \
            "  - scan-file: {}\n".format(spec['scan-file']) + \
            "  - scan-path: {}\n".format(spec['scan-path']) + \
            "  - page:      {}\n".format(spec['page']) + \
            "  - page-dir:  {}\n".format(spec['page-dir']) + \
            "  - page-file: {}\n".format(spec['page-file']) + \
            "  - page-path: {}\n".format(spec['page-path']) + \
            "\n"
        Logger.debug(msg)

        # Console message
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
## =========================================================

## fin.
