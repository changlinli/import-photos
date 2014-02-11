import unittest
import import_photos
import os
import shutil
import subprocess

CURRENT_FILE_DIR = os.path.dirname(os.path.realpath(__file__))
SAMPLE_PHOTO_FOLDER = os.path.join(CURRENT_FILE_DIR, "test_data")
SAMPLE_PHOTO_FULL_PATH = os.path.join(SAMPLE_PHOTO_FOLDER, "IMG_0028.CR2")
SAMPLE_PHOTO_FILENAME = "IMG_0028.CR2"
BUILD_FOLDER = os.path.join(CURRENT_FILE_DIR, "build")

class TestReadEXIFData(unittest.TestCase):
    def setUp(self):
        sample_photo = SAMPLE_PHOTO_FULL_PATH
        self.photo_fp = open(sample_photo, 'rb')

    def test_get_tags(self):
        date_as_list = import_photos.get_img_date(self.photo_fp)
        self.assertEqual(['2014', '01', '01'], date_as_list)

class TestCopyPictures(unittest.TestCase):
    def setUp(self):
        self.destination = os.path.join(CURRENT_FILE_DIR, SAMPLE_PHOTO_FILENAME)

    def test_copy_with_no_flags(self):
        import_photos.side_effects_copy_file_with_flags(SAMPLE_PHOTO_FULL_PATH,
                                                        self.destination)
        isfile_flag = os.path.isfile(self.destination)
        self.assertTrue(isfile_flag)

    def test_copy_if_file_already_exists(self):
        shutil.copyfile(SAMPLE_PHOTO_FULL_PATH, self.destination)
        modified_time_before = os.path.getmtime(self.destination)
        import_photos.side_effects_copy_file_with_flags(SAMPLE_PHOTO_FULL_PATH,
                                                        self.destination)
        modified_time_after = os.path.getmtime(self.destination)
        self.assertEqual(modified_time_before, modified_time_after)

    def tearDown(self):
        try:
            os.remove(self.destination)
        except IOError:
            pass

class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.destination = os.path.join(BUILD_FOLDER, "destination")
        self.destination_with_date = os.path.join(self.destination,
                                                  "2014/01/01")
        self.source = os.path.join(BUILD_FOLDER, "source")
        try:
            os.mkdir(BUILD_FOLDER)
            os.mkdir(self.destination)
            os.mkdir(self.source)

            starting = os.path.join(BUILD_FOLDER, "2014")
            os.mkdir(starting)
            starting = os.path.join(starting, "01")
            os.mkdir(starting)
            starting = os.path.join(starting, "01")
            os.mkdir(starting)
        except OSError:
            pass

    def test_no_optional_flags(self):
        subprocess.call(["python", "import_photos.py", SAMPLE_PHOTO_FOLDER,
                         self.destination])
        isfile_flag = os.path.isfile(os.path.join(self.destination_with_date,
                                                  SAMPLE_PHOTO_FILENAME))
        self.assertTrue(isfile_flag)

    def test_delete_on_copy_option(self):
        new_photo_name = "blah.CR2"
        source_photo_path = os.path.join(self.source, new_photo_name)
        shutil.copyfile(SAMPLE_PHOTO_FULL_PATH, source_photo_path)
        new_photo_path = os.path.join(self.destination_with_date, new_photo_name)
        subprocess.call(["python", "import_photos.py", "-d", self.source,
                         self.destination])
        isfile_flag = os.path.isfile(new_photo_path)
        nofile_flag = not os.path.isfile(source_photo_path)
        self.assertTrue(isfile_flag)
        self.assertTrue(nofile_flag)
        os.remove(new_photo_path)

    def tearDown(self):
        try:
            shutil.rmtree(os.path.join(CURRENT_FILE_DIR, "build"))
        except OSError:
            pass
