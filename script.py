import os
from time import gmtime, strftime
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

directory = '/Users/chenjiping/Library/Mobile Documents/com~apple~CloudDocs/export'

exif_cache = {}

def get_exif_data(file_path):
    if file_path in exif_cache:
        return exif_cache[file_path]
    with Image.open(file_path) as image:
        exif_data = image._getexif()
        exif_cache[file_path] = exif_data
        return exif_data

def read_snap_time(exif_data):
    for tag, value in exif_data.items():
        tag_name = TAGS.get(tag, tag)
        if tag_name == 'DateTimeOriginal':
            return value
    return None

def get_exif_value(exif_data, key):
    for tag, value in exif_data.items():
        tag_name = TAGS.get(tag, tag)
        if tag_name == key:
            return value
    return None

def read_lens_data(exif_data):
    # 镜头信号 镜头制造商 焦距
    return get_exif_value(exif_data, 'LensModel'), get_exif_value(exif_data, 'LensMake'), get_exif_value(exif_data, 'FocalLength')

def read_exposure_info(exif_data):
    # 光圈 快门速度 ISO
    return get_exif_value(exif_data, 'FNumber'), get_exif_value(exif_data, 'ExposureTime'), get_exif_value(exif_data, 'ISOSpeedRatings')

def build_img_ex_info(file_name):
    exif_data = get_exif_data(directory + '/' + file_name)
    lens_data = read_lens_data(exif_data)
    exposure_info = read_exposure_info(exif_data)
    shutter_speed = "1/" + str(round(1 / exposure_info[1], 1))
    if exposure_info[1] >= 1:
        shutter_speed = str(exposure_info[1])
    return f"{lens_data[2]}mm, F{exposure_info[0]}, {shutter_speed}s"

def categorize_files(directory):
    # 初始化结果字典
    series_dict = {}

    # 遍历目录中的所有文件
    for filename in os.listdir(directory):
        if filename.endswith('.jpg') and ' ' in filename:
            # 分离系列名和文件名
            try:
                series_name, file_name = filename.split(' ', 1)
                file_name = file_name.strip()  # 去除前后空白
                # 处理文件名的后缀
                if file_name.endswith('.jpg'):
                    file_name = file_name[:-4]  # 去除 .jpg 后缀
            except ValueError:
                # 如果文件名不符合预期格式，则跳过
                continue

            # 更新字典
            if series_name not in series_dict:
                series_dict[series_name] = []
            series_dict[series_name].append(filename)

    return series_dict

category = categorize_files(directory)

def img_template(file_name):
    with Image.open(directory + '/' + file_name) as img:
      # 根据图片设置宽高比例，获得最好的展示效果
      imgSize = img.size
      width, height = imgSize[0], imgSize[1]
      if height > width: # 竖屏
          height = 960
          width = 540
      elif width > height: # 横屏
          # 2.39:1
          if width / height > 2:
               return f"""
              <figure>
                <img src="https://photo-oss.ismy.wang/{file_name}-comp" alt="{file_name.replace('.jpg', '')}" width="100%" style="aspect-ratio:2.39 / 1" onclick="openModal(this)" loading="lazy" />
                <figcaption>{file_name.replace('.jpg', '')}</figcaption>
                <figcaption>{build_img_ex_info(file_name)} | {read_snap_time(get_exif_data(directory + '/' + file_name))}</figcaption>
              </figure>
              """
          else:
            height = 540
            width = 960
      else:
          height = 800
          width = 800 
      return f"""
              <figure>
                <img src="https://photo-oss.ismy.wang/{file_name}-comp" alt="{file_name.replace('.jpg', '')}" width="100%" height="{height}" onclick="openModal(this)" loading="lazy" />
                <figcaption>{file_name.replace('.jpg', '')}</figcaption>
                <figcaption>{build_img_ex_info(file_name)} | {read_snap_time(get_exif_data(directory + '/' + file_name))}</figcaption>
              </figure>
              """

def post_cmd():
    os.system('git add . ')
    os.system(f'git commit -a -m "update {strftime("%Y-%m-%d %H:%M:%S", gmtime())}"')
    os.system("git push")

def sort_imgs(file_list):
    file_list.sort(key=lambda x: read_snap_time(get_exif_data(directory + '/' + x)), reverse=True)

def fill_template(name, file_list):
    with open('category_template.html', 'r') as f:
        template = f.read()
        template = template.replace('{{name}}', name)
        left = ''
        right = ''
        sort_imgs(file_list)
        for i in range(0, len(file_list)):
            if i % 2 == 0:
                left += img_template(file_list[i])
            else:
                right += img_template(file_list[i])
        return template.replace('{{left}}', left).replace('{{right}}', right)

def index_template(category):
    with open('index_template.html', 'r') as f:
        template = f.read()
        li = ''
        for key in category:
            li += f"""
              <figure>
                <a href="{key}.html">
                  <img src="https://photo-oss.ismy.wang/{category[key][0]}-thumb" loading="lazy"/>
                </a>
                <figcaption>{key}</figcaption>
              </figure>
            """
        return template.replace('{{list}}', li)

for key in category:
    with open(f'{key}.html', 'w') as f:
        f.write(fill_template(key, category[key]))

with open('index.html', 'w') as f:
    f.write(index_template(category))

post_cmd()