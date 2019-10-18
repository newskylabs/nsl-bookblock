"""newskylabs/tools/bookblock/gui/main.py:

The GUI of the bookblock tool.

"""

__author__      = "Dietrich Bollmann"
__email__       = "dietrich@formgames.org"
__copyright__   = "Copyright 2019 Dietrich Bollmann"
__license__     = "Apache License 2.0, http://www.apache.org/licenses/LICENSE-2.0"
__date__        = "2019/10/14"

## =========================================================
## bookblock GUI
## ---------------------------------------------------------

# General Python libs
import sys, os
from pathlib import Path, PosixPath
from os.path import dirname
from time import strftime

# Numpy
import numpy as np

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

from newskylabs.tools.bookblock.utils.settings import Settings
from newskylabs.tools.bookblock.logic.bookblock import BookBlock
from newskylabs.tools.bookblock.kivy.opencvimage import OpenCVImage

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
            Logger.debug("BookBlockApp: Creating config directlry: {}".format(config_dir_name))
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
        log_level  = config.get('logger', 'log_level')
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

        # Log level
        # Command line option --debug overwrites settings
        log_level_option = self._settings.get_debug_level()
        if log_level_option != None:
            log_level = log_level_option

        # Convert to logging debug level
        log_level_code = LOG_LEVELS.get(log_level.lower())

        # When log_level is not one of 
        # trace, debug, info, warning, error, critical, 
        # None is returned.
        if log_level_code == None:
            log_levels = ['trace', 'debug', 'info', 'warning', 'error', 'critical']
            print("ERROR Undefined log level: {}\n".format(log_level) +
                  "Defined are only the following: {}.".format(', '.join(log_levels)),
                  file=sys.stderr)
            exit(-1)

        # Set log level
        Logger.setLevel(log_level_code)

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
        Logger.debug('BookBlockApp: The button <%s> has been pressed' % instance.text)

        img_file = self._image_server.get_previous_page()
        self.show_image(img_file)
        self.update_button_states()

    def next_image(self, instance):
        Logger.debug('BookBlockApp: The button <%s> has been pressed' % instance.text)

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
        Logger.debug('BookBlockApp: The button <%s> has been pressed' % instance.text)

        print("Generating pages:")
        self._image_server.store_pages()
        print("Done.")

## =========================================================
## =========================================================

## fin.
