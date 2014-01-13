import os
import exifread

DEFAULT_STORAGE_DIRECTORY = "/home/username/Pictures"

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
    except FileExistsError:
        pass
    root_path = os.path.join(root_path, head)
    generate_dirs_from_components(path_components, root_path)

def get_img_date(image_fp):
    tags = exifread.process_file(image_fp)
    # This is somewhat brittle, but I always expect the date to be
    # YYYY:MM:DD hr:min:sec
    # and hence am okay with string manipulation instead of IfdTag manipulation
    raw_date = str(tags["EXIF DateTimeDigitized"])
    list_date = raw_date.split(" ")[0].split(":")
    return list_date

if __name__ == "__main__":
    print("Hello!")
