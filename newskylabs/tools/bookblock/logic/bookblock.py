"""newskylabs/tools/bookblock/logic/bookblock.py
   
BookBlock page server.

"""

__author__      = "Dietrich Bollmann"
__email__       = "dietrich@formgames.org"
__copyright__   = "Copyright 2019 Dietrich Bollmann"
__license__     = "Apache License 2.0, http://www.apache.org/licenses/LICENSE-2.0"
__date__        = "2019/10/18"

from kivy.logger import Logger

from newskylabs.tools.bookblock.logic.pages import Pages
from newskylabs.tools.bookblock.logic.page import Page
   
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

    def reset(self):
        self._pages.reset()

    def get_previous_page(self):

        page_spec = self._pages.get_previous_page()
        Logger.debug("BookBlock: page_spec: {}".format(page_spec))
        self._pages.print_current_page()
        page = self._page.get(page_spec)
        Logger.debug("BookBlock: type(page): {}".format(type(page)))
        return page

    def get_current_page(self):

        page_spec = self._pages.get_current_page()
        Logger.debug("BookBlock: page_spec: {}".format(page_spec))
        self._pages.print_current_page()
        page = self._page.get(page_spec)
        Logger.debug("BookBlock: type(page): {}".format(type(page)))
        return page

    def get_next_page(self):

        page_spec = self._pages.get_next_page()
        Logger.debug("BookBlock: page_spec: {}".format(page_spec))
        self._pages.print_current_page()
        page = self._page.get(page_spec)
        Logger.debug("BookBlock: type(page): {}".format(type(page)))
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
## =========================================================

## fin.
