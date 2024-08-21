from PIL.ExifTags import TAGS, GPSTAGS
from PIL import Image

exif_cache = {}
def get_exif_data(file_path):
    if file_path in exif_cache:
        return exif_cache[file_path]
    with Image.open(file_path) as image:
        exif_data = image._getexif()
        exif_cache[file_path] = exif_data
        return exif_data

def read_snap_time(exif_data):
    if not exif_data:
        return ''
    for tag, value in exif_data.items():
        tag_name = TAGS.get(tag, tag)
        if tag_name == 'DateTimeOriginal':
            return value
    return ''

def get_exif_value(exif_data, key):
    if not exif_data:
        return ''
    for tag, value in exif_data.items():
        tag_name = TAGS.get(tag, tag)
        if tag_name == key:
            return value
    return ''

def read_lens_data(exif_data):
    # 镜头信号 镜头制造商 焦距
    return get_exif_value(exif_data, 'LensModel'), get_exif_value(exif_data, 'LensMake'), get_exif_value(exif_data, 'FocalLength')

def read_exposure_info(exif_data):
    # 光圈 快门速度 ISO
    return get_exif_value(exif_data, 'FNumber'), get_exif_value(exif_data, 'ExposureTime'), get_exif_value(exif_data, 'ISOSpeedRatings')

def build_img_ex_info(file_name):
    exif_data = get_exif_data(file_name)
    lens_data = read_lens_data(exif_data)
    exposure_info = read_exposure_info(exif_data)
    shutter_speed = ''
    if exposure_info[1]:
        shutter_speed = "1/" + str(round(1 / exposure_info[1], 1))
    elif exposure_info[1] != '' and exposure_info[1] >= 1:
        shutter_speed = str(exposure_info[1])
    return f"{lens_data[2]}mm, F{exposure_info[0]}, {shutter_speed}s"