"""newskylabs/tools/bookblock/scripts/bookblock.py:

Main of bookblock tool.

Description

bookblock - A tool to cut out pages from a scanned book.

bookblock is a tool to cut out pages from a scanned book.

When scanning a book each scan contains two book pages.  The book
cover on the other side in often consists out of two scans of half the
size showing only the front or back cover.  Further in most cases some
pages might be blanc or not interesting and should be ignored.

bookblock allowes to specify the size and offset of a page
bounding box and a specification of the pages which should be
extracted.  The pages then can be previewed and finally cut out of the
scan and saved to disk.

"""

__author__      = "Dietrich Bollmann"
__email__       = "dietrich@formgames.org"
__copyright__   = "Copyright 2019 Dietrich Bollmann"
__license__     = "Apache License 2.0, http://www.apache.org/licenses/LICENSE-2.0"
__date__        = "2019/10/17"

import sys, os, click

from newskylabs.tools.bookblock.utils.settings import Settings
from newskylabs.tools.bookblock.utils.generic import get_version_long

# -i, --source-dir
option_source_dir_help = "Directory where the scans are stored."
option_source_dir_default = "/tmp"

# -o, --target-dir
option_target_dir_help = "Directory where the pages should be stored."
option_target_dir_default = "/tmp"

# -i, --source-file_format
option_source_file_format_help = "File name format of the scans."
option_source_file_format_default = 'scan%03d.png'

# -o, --target-file_format
option_target_file_format_help = "File name format for the pages."
option_target_file_format_default = 'page%03d.png'

# -p, --pages
option_pages_help = "Specification of the pages to be cut out."
option_pages_default = '1r,2-9lr,10l'

# -g, --geometry
option_geometry_help = "Geometry of the pages."
option_geometry_default = '600x800+10+20'

# -c, --image-mode
option_image_mode_help = "Should I generate color or grayscale images?"
option_image_mode_choice = ['color', 'grayscale']
option_image_mode_default = 'color'

# -v, --view-mode
option_view_mode_help = "View mode: " + \
    "either show the scan with a bounding box marking the page - " + \
    "or the resulting page."
option_view_mode_choice = ['scan', 'page']
option_view_mode_default = 'page'

# -e, --examples
option_examples_help = "Show some usage examples."
option_examples_default = False

# -d, --debug
option_debug_help = "Set the log level."
option_debug_choice = ['trace', 'debug', 'info', 'warning', 'error', 'critical']
option_debug_default = 'warning'

command_context_settings={'help_option_names': ['-h', '--help']}

@click.command(context_settings=command_context_settings)

@click.option('-i', '--source-dir',
              type=click.Path(exists=True), 
              default=option_source_dir_default,
              help=option_source_dir_help)

@click.option('-o', '--target-dir',
              type=click.Path(exists=True), 
              default=option_target_dir_default,
              help=option_target_dir_help)

@click.option('-s', '--source-file-format', 
              default=option_source_file_format_default,
              help=option_source_file_format_help)

@click.option('-t', '--target-file-format',
              default=option_target_file_format_default,
              help=option_target_file_format_help)
  
@click.option('-p', '--pages',
              default=option_pages_default,
              help=option_pages_help)
  
@click.option('-g', '--geometry',
              default=option_geometry_default,
              help=option_geometry_help)

@click.option('-c', '--image-mode', 
              type=click.Choice(option_image_mode_choice),
              default=option_image_mode_default, 
              help=option_image_mode_help)

@click.option('-v', '--view-mode',
              type=click.Choice(option_view_mode_choice),
              default=option_view_mode_default, 
              help=option_view_mode_help)

@click.option('-e', '--examples',
              is_flag=True,
              default=option_examples_default,
              help=option_examples_help)

@click.option('-d', '--debug',
              type=click.Choice(option_debug_choice),
              default=option_debug_default,
              help=option_debug_help)

@click.version_option(get_version_long(), '-V', '--version')

def bookblock(source_dir, target_dir, 
              source_file_format, target_file_format,
              pages,
              geometry,
              image_mode, 
              view_mode,
              examples, 
              debug):
    """Cut out pages from book scans.
    """
    
    # Resetting `sys.argv':
    # 
    # The bookblock command line options disturb Kivy:
    # See file site-packages/kivy/__init__.py :
    # 
    #     try:
    #         opts, args = getopt(sys_argv[1:], 'hp:fkawFem:sr:dc:', [
    #             'help', 'fullscreen', 'windowed', 'fps', 'event',
    #             'module=', 'save', 'fake-fullscreen', 'auto-fullscreen',
    #             'multiprocessing-fork', 'display=', 'size=', 'rotate=',
    #             'config=', 'debug', 'dpi='])
    # 
    #     except GetoptError as err:
    #         Logger.error('Core: %s' % str(err))
    #         kivy_usage()
    # 
    # Example: the option `--source-dir <dir>' causes the following error:
    # 
    #   Core: option --source-dir not recognized
    # 
    # Therefore only options relevant for Kivy should be 
    # contained in sys.argv when starting to deal with Kivy code:
    sys.argv = [ sys.argv[1] ]

    if debug in ['trace', 'debug', 'info']:
        print("DEBUG bookblock:")
        print("")
        print("  - source_dir:         {}".format(source_dir))
        print("  - target_dir:         {}".format(target_dir))
        print("  - source_file_format: {}".format(source_file_format))
        print("  - target_file_format: {}".format(target_file_format))
        print("  - pages:              {}".format(pages))
        print("  - geometry:           {}".format(geometry))
        print("  - image_mode:         {}".format(image_mode))
        print("  - view_mode:          {}".format(view_mode))
        print("  - examples:           {}".format(examples))
        print("  - debug:              {}".format(debug))

    # Show examples?
    if examples:
        print_examples()
        exit()

    # Settings
    settings = Settings() \
        .set_debug_level(debug) \
        .set_image_mode(image_mode) \
        .set_view_mode(view_mode) \
        .set_source_dir(source_dir) \
        .set_target_dir(target_dir) \
        .set_source_file_format(source_file_format) \
        .set_target_file_format(target_file_format) \
        .set_geometry(geometry) \
        .set_pages(pages)

    # Print settings
    settings.print_settings()

    # Hack to silently import Kivy's noisy logger:
    # The logger prints all kind of messages before the log level can be set
    # and seems to ignore its config file log level settings as well
    # (Kivy's config is at ~/.kivy/config.ini)
    if not debug in ['trace', 'debug', 'info']:

        # Silence stderr
        orig_stderr = sys.stderr
        sys.stderr = open(os.devnull, "w")

        # Import Kivy's logger
        from kivy.logger import Logger, LOG_LEVELS

        # Set the log level
        Logger.setLevel(level=LOG_LEVELS.get(debug))

        # Restore stdout
        sys.stderr = orig_stderr

    # Start the GUI
    # For some reason BookBlockApp cannot be imported before
    # as it seems to interfere with click
    from newskylabs.tools.bookblock.gui.main import BookBlockApp
    app = BookBlockApp(settings)
    app.run()

    # done :)
    print("")
    print("Bye :)")
    print("")
    exit()
           
## =========================================================
## Main
## ---------------------------------------------------------
 
def print_examples():
    """Print examples."""
    print("""
Examples:

Generate color pages
from the left and right side of scan 0 to 99:

bookblock \\
  --debug              trace \\
  --source-dir         ~/home/tmp/the-secret-garden/png \\
  --target-dir         ~/home/tmp/pages \\
  --source-file-format the-secret-garden.%02d.png \\
  --target-file-format page%02d.png \\
  --geometry           1000x1600+22+41 \\
  --pages              0-99lr \\
  --image-mode         color \\
  --view-mode          scan

Generate color pages from
the left sides of scan 0 and 1 and
both sides of the scans 2 to 56:

bookblock \\
  --debug              info \\
  --source-dir         ~/home/tmp/the-secret-garden/png \\
  --target-dir         ~/home/tmp/pages \\
  --source-file-format the-secret-garden.%02d.png \\
  --target-file-format page%02d.png \\
  --geometry           1000x1600+22+41 \\
  --pages              0-1l,2-56lr \\
  --image-mode         color \\
  --view-mode          scan

Generate color pages from
the left sides of scan 0 and 1,
the right sides of scan 2, 6 and 7,
both sides of the scans 8 to 9 and
both sides of the scans 45 to 46:

bookblock \\
  --debug              warning \\
  --source-dir         ~/home/tmp/the-secret-garden/png \\
  --target-dir         ~/home/tmp/pages \\
  --source-file-format the-secret-garden.%02d.png \\
  --target-file-format page%02d.png \\
  --geometry           1000x1600+22+41 \\
  --pages              0-1l,2r,6r,7r,8-9lr,45-46lr \\
  --image-mode         color \\
  --view-mode          scan

Generate grayscale pages from
the left sides of scan 0 and 1,
the right sides of scan 2, 6 and 7,
both sides of the scans 8 to 46:

bookblock \\
  --source-dir         ~/home/tmp/the-secret-garden/png \\
  --target-dir         ~/home/tmp/pages \\
  --source-file-format the-secret-garden.%02d.png \\
  --target-file-format page%02d.png \\
  --geometry           1000x1600+22+41 \\
  --pages              0-1l,2r,6r,7r,8-46lr \\
  --image-mode         grayscale \\
  --view-mode          scan

""")

## =========================================================
## =========================================================

## fin.
