"""newskylabs/tools/bookblock/utils/settings.py

Settings.

"""

__author__      = "Dietrich Bollmann"
__email__       = "dietrich@formgames.org"
__copyright__   = "Copyright 2019 Dietrich Bollmann"
__license__     = "Apache License 2.0, http://www.apache.org/licenses/LICENSE-2.0"
__date__        = "2019/10/16"

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
## =========================================================

## fin.
