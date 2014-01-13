from __future__ import print_function
import os
import exifread
import shutil
import argparse

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

PICTURE_FILE_EXTENSIONS = [".jpg", ".jpeg", ".tif", ".tiff", ".cr2"]
# First element of the pair refers to the metadata file for a given movie file
# while the second element is the actual movie file
MOVIE_FILE_EXTENSIONS = [(".thm", ".mov")]
MOVIE_DATA_EXTENSIONS = [x for (x, y) in MOVIE_FILE_EXTENSIONS]

if __name__ == "__main__":
    argument_description="Import photos from camera to folders"
    argument_parser = argparse.ArgumentParser(description=argument_description)
    argument_parser.add_argument('source', metavar='S', type=str,
                                 help='Source from which to import photos')
    argument_parser.add_argument('destination', metavar='D', type=str,
                                 help='Destination to place imported photos')
    args = argument_parser.parse_args()
    source = args.source
    destination = args.destination

    for root, dirs, files in os.walk(source):
        for name in files:
            extension = os.path.splitext(name)[1]
            if extension.lower() in PICTURE_FILE_EXTENSIONS:
                filename = os.path.join(root, name)
                fp = open(filename, 'rb')
                date = get_img_date(fp)
                fp.close()
                # Pass date list by value, not reference so date isn't destroyed
                generate_dirs_from_components(date[:], destination)
                destination_file = os.path.join(*([destination] + 
                                                  date +
                                                  [name]))
                print("Copying {0} to {1}... ".
                      format(filename, destination_file),
                      end="")
                shutil.copyfile(filename, destination_file)
                print("Done!")
            elif extension.lower() in MOVIE_DATA_EXTENSIONS:
                print("Video here!")
            else:
                pass
