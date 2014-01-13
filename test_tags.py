import import_photos

sample_photo = "/home/changlin/Pictures/2014/01/01/IMG_0028.CR2"
fp = open(sample_photo, 'rb')
print(import_photos.get_img_date(fp))
