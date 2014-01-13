import unittest
import import_photos

class TestReadEXIFData(unittest.TestCase):
    def setUp(self):
        sample_photo = "test_data/IMG_0028.CR2"
        self.photo_fp = open(sample_photo, 'rb')

    def test_get_tags(self):
        date_as_list = import_photos.get_img_date(self.photo_fp)
        self.assertEqual(['2014', '01', '01'], date_as_list)
