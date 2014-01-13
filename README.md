import_photos.py
================

A short little script to import photos from a digital camera into folders by
date based on EXIF data.  This was originally inspired by the way that Shotwell
imports photos. However, because I do very little editing in Shotwell (instead
relying on Darktable and GIMP), it made very little sense for me to go through
the huge overhead of Shotwell's importing process when I really just wanted the
files copied from one place to another and organized intelligently into folders.
Hence I wrote this short script.

To use, simply run `python import_photos.py -h` and a description will appear.

Installing
----------

Simply run (preferably within a virtualenv) `pip install -r requirements.txt`.
Note that unfortunately due to the dependency on `exifread`, this is a Python 2
script. Ideally I'll move to Python 3 soon to keep up with the future!

Testing
-------

To run the tests both in the docstrings and in the `tests.py` file, simply run
`nosetests --with-doctest`.
