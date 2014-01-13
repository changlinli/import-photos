from __future__ import print_function
import os
import exifread
import shutil
import argparse
import hashlib
import datetime
import sys
import functools as ft

DEFAULT_STORAGE_DIRECTORY = "/home/user/Pictures"

def split_components(pathname):
    """
    Split a pathname into its components.

    Note that pathname cannot end in a slash!

    >>> split_components("/root/blah/wer")
    ['root', 'blah', 'wer']
    """
    head, tail = os.path.split(pathname)
    if head == "" or head == "/":
        return [tail]
    else:
        components = split_components(head)
        components.append(tail)
        return components

def generate_dirs_from_components(path_components, root_path):
    """
    Recursively generate directories from list of path components.

    >>> generate_dirs_from_components(["a", "b", "c"], "/root") #doctest: +SKIP
    ... #Generates /root/a/b/c
    None
    """
    if path_components == []:
        return None
    head = path_components.pop(0)
    try:
        os.mkdir(os.path.join(root_path, head))
    except OSError:
        pass
    root_path = os.path.join(root_path, head)
    generate_dirs_from_components(path_components, root_path)

def get_img_date(image_fp):
    """
    Based on the EXIF data of an image, return the date it was taken as a list
    with ['YYYY', 'MM', 'DD']
    """
    tags = exifread.process_file(image_fp)
    # This is somewhat brittle, but I always expect the date to be
    # YYYY:MM:DD hr:min:sec
    # and hence am okay with string manipulation instead of IfdTag manipulation
    raw_date = str(tags["EXIF DateTimeDigitized"])
    list_date = raw_date.split(" ")[0].split(":")
    return list_date

def file_to_hash(filename):
    md5 = hashlib.md5()
    with open(filename, 'rb') as fp:
        # Use multiples of 128 bytes for best results with MD5
        for portion in iter(ft.partial(fp.read, 8192), ''):
            md5.update(portion)
    return md5.digest()


PICTURE_FILE_EXTENSIONS = [".jpg", ".jpeg", ".tif", ".tiff", ".cr2"]
# First element of the pair refers to the metadata file for a given movie file
# while the second element is the actual movie file
MOVIE_FILE_EXTENSIONS = [(".thm", ".mov")]
MOVIE_DATA_EXTENSIONS = [x for (x, y) in MOVIE_FILE_EXTENSIONS]

if __name__ == "__main__":
    # Setting up the argument parser
    argument_description="Import photos from camera to folders"
    argument_parser = argparse.ArgumentParser(description=argument_description)
    argument_parser.add_argument("-v", "--verbose", action="store_true",
                                 help="Turn on verbose printing")
    argument_parser.add_argument("-l", "--log", action="store_true",
                                 help="Turn on logging (log file will be in"
                                 " destination directory)")
    argument_parser.add_argument("source", metavar="S", type=str,
                                 help="Source from which to import photos")
    argument_parser.add_argument("destination", metavar="D", type=str,
                                 help="Destination to place imported photos")
    args = argument_parser.parse_args()
    source = args.source
    destination = args.destination
    verbose = args.verbose
    logging = args.log
    LOG_NAME = "import_pics.log"

    # Performing preliminary checks and preparation
    if not os.path.isdir(destination):
        print("Error: The destination needs to be a directory!")
        sys.exit(1)
    if logging:
        log_file = open(os.path.join(destination, LOG_NAME), "w")
        log_file.write(str(datetime.datetime.now()) + "\n")

    # Actually doing the work
    for root, dirs, files in os.walk(source):
        for name in files:
            extension = os.path.splitext(name)[1]
            if extension.lower() in PICTURE_FILE_EXTENSIONS:
                filename = os.path.join(root, name)
                fp = open(filename, "rb")
                date = get_img_date(fp)
                fp.close()
                # Pass date list by value, not reference so date isn't destroyed
                generate_dirs_from_components(date[:], destination)
                destination_file = os.path.join(*([destination] + 
                                                  date +
                                                  [name]))
                beginning_string = "Copying {0} to {1}... ".format(filename, destination_file)
                if verbose:
                    print(beginning_string, end="")

                before_copy_hash = file_to_hash(filename)
                shutil.copyfile(filename, destination_file)

                ending_string = "Done!"
                if verbose:
                    print(ending_string)
                if logging:
                    log_file.write(beginning_string + ending_string + "\n")

                after_copy_hash = file_to_hash(destination_file)
                if before_copy_hash == after_copy_hash:
                    hash_string = "Hashes match!"
                else:
                    hash_string = ("Warning: {0}'s and {1}'s hashes do not"
                    "match!".format(filename, destination_file))
                    print(hash_string)
                if logging:
                    log_file.write(hash_string + "\n")

            elif extension.lower() in MOVIE_DATA_EXTENSIONS:
                print("Video here! (I'll add more functionality for this later!)")
            else:
                pass
