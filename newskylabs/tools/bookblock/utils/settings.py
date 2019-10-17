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
        self._debug_level        = None
        self._image_mode         = None
        self._view_mode          = None
        self._source_dir         = None
        self._target_dir         = None
        self._source_file_format = None
        self._target_file_format = None
        self._geometry           = None
        self._pages              = None

    def print_settings(self):

        print("")
        print("Settings:")
        print("")
        print("  - source_dir:         ", self._source_dir)
        print("  - target_dir:         ", self._target_dir)
        print("  - source_file_format: ", self._source_file_format)
        print("  - target_file_format: ", self._target_file_format)
        print("  - pages:              ", self._pages)
        print("  - geometry:           ", self._geometry)
        print("  - image mode:         ", self._image_mode)
        print("  - view mode:          ", self._view_mode)        
        print("  - debug_level:        ", self._debug_level)
        print("")

    ## Setters

    def set_debug_level(self, debug_level):
        self._debug_level = debug_level
        return self

    def set_image_mode(self, image_mode):
        self._image_mode = image_mode
        return self

    def set_view_mode(self, view_mode):
        self._view_mode = view_mode
        return self

    def set_source_dir(self, source_dir):
        self._source_dir = source_dir
        return self

    def set_target_dir(self, target_dir):
        self._target_dir = target_dir
        return self

    def set_source_file_format(self, source_file_format):
        self._source_file_format = source_file_format
        return self

    def set_target_file_format(self, target_file_format):
        self._target_file_format = target_file_format
        return self

    def set_geometry(self, geometry):
        self._geometry = geometry
        return self

    def set_pages(self, pages):
        self._pages = pages
        return self

    ## Getters

    def get_debug_level(self):
        return self._debug_level

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
