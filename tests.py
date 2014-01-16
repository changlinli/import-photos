import unittest
import import_photos
import os
import shutil

CURRENT_FILE_DIR = os.path.dirname(os.path.realpath(__file__))
SAMPLE_PHOTO_LOCATION = os.path.join(CURRENT_FILE_DIR, "test_data/IMG_0028.CR2")
SAMPLE_PHOTO_FILENAME = "IMG_0028.CR2"

class TestReadEXIFData(unittest.TestCase):
    def setUp(self):
        sample_photo = SAMPLE_PHOTO_LOCATION
        self.photo_fp = open(sample_photo, 'rb')

    def test_get_tags(self):
        date_as_list = import_photos.get_img_date(self.photo_fp)
        self.assertEqual(['2014', '01', '01'], date_as_list)

class TestCopyPictures(unittest.TestCase):
    def setUp(self):
        self.destination = os.path.join(CURRENT_FILE_DIR, SAMPLE_PHOTO_FILENAME)
    def test_copy_with_no_flags(self):
        import_photos.side_effects_copy_file_with_flags(SAMPLE_PHOTO_LOCATION,
                                                        self.destination)
        isfile_flag = os.path.isfile(self.destination)
        self.assertTrue(isfile_flag)
    def test_copy_if_file_already_exists(self):
        shutil.copyfile(SAMPLE_PHOTO_LOCATION, self.destination)
        modified_time_before = os.path.getmtime(self.destination)
        import_photos.side_effects_copy_file_with_flags(SAMPLE_PHOTO_LOCATION,
                                                        self.destination)
        modified_time_after = os.path.getmtime(self.destination)
        self.assertEqual(modified_time_before, modified_time_after)
    def tearDown(self):
        try:
            os.remove(self.destination)
        except IOError:
            pass
