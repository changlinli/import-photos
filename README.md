import_photos.py
================

A short little script to import photos from a digital camera into folders by
date based on EXIF data.  This was originally inspired by the way that Shotwell
imports photos. However, because I do very little editing in Shotwell (instead
relying on Darktable and GIMP), it made very little sense for me to go through
the huge overhead of Shotwell's importing process when I really just wanted the
files copied from one place to another and organized intelligently into folders.
Hence I wrote this short script.

This script hashes both files to ensure that copying went well and also can
delete photos that have already been imported and has a list of other options as
well.

Some examples of usage are as follows;

+ In the simplest case, we can simply do

    import_photos.py /media/DIGITAL_CAMERA/DCIS ~/Pictures

which imports all photos from one's digital camera (assuming that it's standards
compliant and stores all its photos in a folder labeled DCIS). This includes
hashing before and after copying and comparing hashes out of the box.

For other uses, simply run `python import_photos.py -h` and a description will
appear.

Dependencies
------------

In order to build this script you'll need a Python interpreter. I've only tested
this on Python 2.7.x so I can only vouch for its accuracy on those Python
systems.  Note that unfortunately due to the dependency on `exifread`, this is a
Python 2 script. Ideally I'll move to Python 3 soon to keep up with the future!

You'll need `pip` as well.

`make` would also be nice, otherwise you can just manually execute the commands
in `Makefile.default`.

I've only tested this on Debian jessie, but it should work on any Linux system.
It will probably work on Macs and a BSD system. It _might_ work on Windows. If
you're on Windows, you'll need to make the usual translations from Unix-style
commands to Windows commands in the `Makefile.default` file.

Installing
----------

Rename `Makefile.default` as `Makefile`. Then run

    make first_install

. You should find an executable called `import_photos` in a new `dist` folder.

Testing
-------

To run the tests both in the docstrings and in the `tests.py` file, simply run
`nosetests --with-doctest`.

Occasionally the first run of the tests will fail, but subsequent runs will
succeed. I have not spent the time to track down why this is the case.
