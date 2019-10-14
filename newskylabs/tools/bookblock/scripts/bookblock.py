#!/usr/bin/env python
## =========================================================
##                    Dietrich Bollmann, Luebeck, 2019/10/11
## 
## bookblock
## 
## Cutting pages from book scans...
## ---------------------------------------------------------

'''* bookblock - A tool to cut out pages from a scanned book.

** Description

bookblock is a tool to cut out pages from a scanned book.

When scanning a book each scan contains two book pages.  The book
cover on the other side in often consists out of two scans of half the
size showing only the front or back cover.  Further in most cases some
pages might be blanc or not interesting and should be ignored.

bookblock allowes to specify the size and offset of a page
bounding box and a specification of the pages which should be
extracted.  The pages then can be previewed and finally cut out of the
scan and saved to disk.

** Usage

TODO

'''

import sys
import getopt

from newskylabs.tools.bookblock.gui.main import debug, Settings, BookBlockApp

## =========================================================
## usage
## ---------------------------------------------------------

def usage(command=None):

    if command == 'block':
        ## =====================================
        ## bookblock block
        ## -------------------------------------
        error_msg = """bookblock block - bla bla bla...

A simple python template :)

options:

  -h, --help                           - Print this help text.
  -m, --mode                           - View mode - one of: raw, bb, page
                                         raw  - The scan;
                                         bb   - The scan with bounding box;
                                         page - The page extracted from the scan 
                                                corresponding to the bounding box.
  -d, --debug                          - Debug mode.

  -i, --source-dir                     - Directory where the scans are stored.
  -o, --target-dir                     - Directory where the cutted pages 
                                         should be stored.
  -s, --source-file-format <format>    - File name format of the scans.
  -t, --target-file-format <format>    - File name format for the pages.
  -g, --geometry           <geometry>  - Geometry of the page bounding box.
  -p, --pages                          - Specification for the pages to be 
                                         cut out.
  -c, --image-mode                     - Image mode - one of: color, grayscale
  -v, --view-mode                      - View mode - one of: page, scan

Examples:

# Color, more pages than existing:

bookblock block \\
  --debug \\
  --source-dir         ~/home/tmp/the-secret-garden/png \\
  --target-dir         ~/home/tmp/pages \\
  --source-file-format the-secret-garden.%02d.png \\
  --target-file-format page%02d.png \\
  --geometry           1000x1600+22+41 \\
  --pages              0-100lr \\
  --mode               bb \\
  --image-mode         color \\
  --view-mode          scan

# Color, only existing pages:

bookblock block \\
  --debug \\
  --source-dir         ~/home/tmp/the-secret-garden/png \\
  --target-dir         ~/home/tmp/pages \\
  --source-file-format the-secret-garden.%02d.png \\
  --target-file-format page%02d.png \\
  --geometry           1000x1600+22+41 \\
  --pages              0-1l,2-56lr \\
  --mode               bb \\
  --image-mode         color \\
  --view-mode          scan

# Color, only required pages, 
# skipping most of them in the middle:

bookblock block \\
  --debug \\
  --source-dir         ~/home/tmp/the-secret-garden/png \\
  --target-dir         ~/home/tmp/pages \\
  --source-file-format the-secret-garden.%02d.png \\
  --target-file-format page%02d.png \\
  --geometry           1000x1600+22+41 \\
  --pages              0-1l,2r,6r,7r,8-9lr,45-46lr \\
  --mode               bb \\
  --image-mode         color \\
  --view-mode          scan

# Black and white, all required pages:
# final version

bookblock block \\
  --source-dir         ~/home/tmp/the-secret-garden/png \\
  --target-dir         ~/home/tmp/pages \\
  --source-file-format the-secret-garden.%02d.png \\
  --target-file-format page%02d.png \\
  --geometry           1000x1600+22+41 \\
  --pages              0-1l,2r,6r,7r,8-46lr \\
  --mode               bb \\
  --image-mode         grayscale \\
  --view-mode          scan

"""
    else:
        ## =====================================
        ## bookblock - no or undefined command
        ## -------------------------------------
        error_msg = """bookblock -- cut scanned pages

Usage: bookblock <command> [<arguments> ...]

The following commands are defined:

  block - Cut out a "book block"

Examples:

bookblock block --help
"""

    print(error_msg, file=sys.stderr)

## =========================================================
## bookblock_main()
## ---------------------------------------------------------

def bookblock_main(args):

    try:
        opts, args = getopt.getopt(args, "hdi:o:s:t:g:p:m:c:v:",
                                   ["help", "debug", 
                                    "source-dir=", "target-dir=", 
                                    "source-file-format=", "target-file-format=",
                                    "geometry=",
                                    "pages=",
                                    "mode=",
                                    "image-mode=",
                                    "view-mode="
                                   ])
        
    except getopt.GetoptError as err:
        # print help information and exit:
        print(str(err)) # will print something like "option -a not recognized"
        usage(command='block')

        sys.exit(2)

    # Settings
    settings = Settings()

    # Global settings variable
    global g_settings 
    g_settings = settings

    for o, a in opts:

        if o in ('-h', '--help'):
            usage(command='block')
            sys.exit()

        elif o in ('-d', '--debug'):
            debug("Debug mode on!")
            settings.set_debug_mode(debug)

        elif o in ('-i', '--source-dir'):
            source_dir = a
            settings.set_source_dir(source_dir)

        elif o in ('-o', '--target-dir'):
            target_dir = a
            settings.set_target_dir(target_dir)

        elif o in ('-s', '--source-file-format'):
            source_file_format = a
            settings.set_source_file_format(source_file_format)

        elif o in ('-t', '--target-file-format'):
            target_file_format = a
            settings.set_target_file_format(target_file_format)

        elif o in ('-g', '--geometry'):
            geometry = a
            settings.set_geometry(geometry)

        elif o in ('-p', '--pages'):
            pages = a
            settings.set_pages(pages)

        elif o in ('-m', '--mode'):
            mode = a
            settings.set_mode(mode)

        elif o in ('-m', '--image-mode'):
            image_mode = a
            settings.set_image_mode(image_mode)

        elif o in ('-v', '--view-mode'):
            view_mode = a
            settings.set_view_mode(view_mode)

        else:
            assert False, 'Unknown option: {}'.format(o)

    # Print settings
    settings.print_settings()
    
    # Start the GUI
    app = BookBlockApp(settings)
    app.run()

    # done :)
    print("")
    print("Bye :)")
    print("")
    exit()
            
## =========================================================
## main
## ---------------------------------------------------------

def bookblock():


    # When no command has been given
    if len(sys.argv) < 2:
        usage()
        sys.exit(-1)

    # Extract command and arguments
    command = sys.argv[1]
    args = sys.argv[2:]

    # Call the function corresponding to the given command
    if command == 'block':
        # Cut out a "book block":
        # Cut out left and right pages
        # from the specified list of copies
        # using the given offset and page size.
        bookblock_main(args)

    else:
        # Unknown command
        print("ERROR Unknown command: {}".format(command), file=sys.stderr)
        usage()
        sys.exit(-1)

## =========================================================
## When executed as script
## ---------------------------------------------------------
 
if __name__ == '__main__':
    bookblock()

## =========================================================
## =========================================================

## fin
