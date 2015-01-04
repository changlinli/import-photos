from __future__ import print_function
import os
import exifread
import shutil
import argparse
import hashlib
import datetime
import sys
import functools as ft
import logging

DEFAULT_STORAGE_DIRECTORY = os.environ["HOME"]

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

def file_to_hash(filename, chunk_size=16777216):
    """
    Hashes a file chunk by chunk according to chunk_size (so as to minimize
    memory usage). Note that chunk_size should be a multiple of 128 bytes for
    best results with MD5.
    """
    md5 = hashlib.md5()
    with open(filename, 'rb') as fp:
        # Use multiples of 128 bytes for best results with MD5
        for portion in iter(ft.partial(fp.read, chunk_size), ''):
            md5.update(portion)
    return md5.digest()

def recursive_read_img_data(source_dir):
    """
    Recursively create a list of all the data associated with the images.
    """
    return

def side_effects_copy_file_with_flags(source,
                                      destination,
                                      verbose_flag=False,
                                      log_deletes_flag=False,
                                      log_deletes_file=None,
                                      delete_on_copy_flag=False,
                                      fast_skip_flag=False):
    """
    Monster function which copies all the files. This hopefully will be broken
    up at some point, but right now acts as a common block of code for both
    copying images and videos.
    """

    beginning_string = "Copying {0} to {1}... ".format(source, destination)
    if verbose_flag:
        print(beginning_string)

    before_copy_hash = None
    try:
        skip_message = ("It looks like {0} already exists; skipping it... ".
                        format(destination))
        if fast_skip_flag and os.path.isfile(destination):
            if verbose_flag:
                print(skip_message)
            logging.info(skip_message)
            if delete_on_copy_flag:
                delete_string = "Deleting {0}".format(source)
                if verbose_flag:
                    print(delete_string)
                logging.info(delete_string)
                os.remove(source)
            return
        elif (file_to_hash(destination) == file_to_hash(source) and 
              not fast_skip_flag):
            if verbose_flag:
                print(skip_message)
            logging.info(skip_message)
            if delete_on_copy_flag:
                delete_string = "Deleting {0}".format(source)
                if verbose_flag:
                    print(delete_string)
                logging.info(delete_string)
                os.remove(source)
            return
    except IOError:
        before_copy_hash = file_to_hash(source)
        shutil.copyfile(source, destination)

    ending_string = "Done!"
    if verbose_flag:
        print(ending_string)
    logging.info(beginning_string + ending_string)

    after_copy_hash = file_to_hash(destination)
    if before_copy_hash == after_copy_hash:
        hash_string = "Hashes match!"
        if delete_on_copy_flag:
            delete_string = "Deleting {0}".format(source)
            if verbose_flag:
                print(delete_string)
            logging.info(delete_string)
            os.remove(source)
    else:
        hash_string = ("Warning: {0}'s and {1}'s hashes do not"
        "match!".format(source, destination))
        print(hash_string)
    logging.info(hash_string)


PICTURE_FILE_EXTENSIONS = [".jpg", ".jpeg", ".tif", ".tiff", ".cr2"]
# First element of the pair refers to the metadata file for a given movie file
# while the second element is the actual movie file
# Also this is ugly I know, but Magic Lantern spits out weird file suffixes.
# Eventually I may switch over to a regex.
MOVIE_FILE_EXTENSIONS = [(".thm", ".mov"),
                         ("", ".raw"),
                         ("", ".mlv"),
                         ("", ".m00"),
                         ("", ".m01"),
                         ("", ".m02"),
                         ("", ".m03"),
                         ("", ".m04"),
                         ("", ".m05"),
                         ("", ".m06"),
                         ("", ".m07"),
                         ("", ".m08"),
                         ("", ".m09")]
MOVIE_DATA_EXTENSIONS = [y for (x, y) in MOVIE_FILE_EXTENSIONS]

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

    argument_parser.add_argument("-d", "--delete-on-copy", action="store_true",
                                 help="Delete a file after it has been"
                                 " successfully copied. Note deletion will"
                                 " not occur if the hashes of the copied file"
                                 " and the source file do not match. Therefore"
                                 " this option is not compatible with"
                                 " --fast-skip")

    argument_parser.add_argument("-f", "--fast-skip", action="store_true",
                                 help="Skip any files that already exist in the"
                                 " destination without checking whether the"
                                 " hash of the destination file and the source"
                                 " file match.")

    args = argument_parser.parse_args()
    source = args.source
    destination = args.destination
    verbose = args.verbose
    delete_on_copy = args.delete_on_copy
    if args.log:
        logging.basicConfig(filename=os.path.join(destination, "import_pics.log"),
                            level=logging.INFO,
                            format="%(levelname)s:%(message)s:%(asctime)s")
        logging.info(datetime.datetime.now())
    fast_skip = args.fast_skip

    # Performing preliminary checks and preparation
    if not os.path.isdir(destination):
        print("Error: The destination needs to be a directory!")
        sys.exit(1)

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
                side_effects_copy_file_with_flags(source=filename,
                                                  destination=destination_file,
                                                  verbose_flag=verbose,
                                                  delete_on_copy_flag=delete_on_copy,
                                                  fast_skip_flag=fast_skip)

            elif extension.lower() in MOVIE_DATA_EXTENSIONS:
                filename = os.path.join(root, name)
                # Note that ctime is NOT creation time on UNIX platforms, but
                # rather when the metadata is changed
                ctime = os.path.getctime(filename)
                year = datetime.datetime.fromtimestamp(ctime).year
                month = datetime.datetime.fromtimestamp(ctime).month
                day = datetime.datetime.fromtimestamp(ctime).day
                date = [str(year), str(month), str(day)]
                generate_dirs_from_components(date[:], destination)
                destination_file = os.path.join(*([destination] + 
                                                  date + 
                                                  [name]))
                side_effects_copy_file_with_flags(source=filename,
                                                  destination=destination_file,
                                                  verbose_flag=verbose,
                                                  delete_on_copy_flag=delete_on_copy,
                                                  fast_skip_flag=fast_skip)
            else:
                pass
