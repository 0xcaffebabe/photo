import os
from time import gmtime, strftime
from PIL import Image

from exif import build_img_ex_info, get_exif_data, read_snap_time

directory = '../photo-data'

page_size = 2


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
                <figcaption>{build_img_ex_info(directory + '/' + file_name)} | {read_snap_time(get_exif_data(directory + '/' + file_name))}</figcaption>
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
                <figcaption>{build_img_ex_info(directory + '/' + file_name)} | {read_snap_time(get_exif_data(directory + '/' + file_name))}</figcaption>
              </figure>
              """

def sort_imgs(file_list):
    file_list.sort(key=lambda x: read_snap_time(get_exif_data(directory + '/' + x)), reverse=True)

# 计算页数
def calc_pages(file_list):
    if len(file_list) % page_size == 0:
        return len(file_list) // page_size
    return len(file_list) // page_size + 1

def generate_page_html(page_num, category, total_page):
    html = ''
    for i in range(1, total_page + 1):
        if i == 1:
            html += f'<a href="/{category}.html" class="{ "active" if i == page_num else ""}">{i}</a>\n'
        else:
            html += f'<a href="/pages/{category}{i}.html" class="{ "active" if i == page_num else ""}">{i}</a>\n'
    return html

def category_template(name, file_list):
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

def write_category():
    for key in category:
        file_list = category[key]
        for page_num in range(1, calc_pages(file_list) + 1):
            template = category_template(key, file_list[(page_num-1)*page_size:page_num*page_size])
            if calc_pages(file_list)  == 1:
                template = template.replace('{{pages}}', '')
            else:
                template = template.replace('{{pages}}', generate_page_html(page_num, key, calc_pages(file_list)))
            if page_num == 1:
                with open(f'{key}.html', 'w') as f:
                    f.write(template)
            else:
                with open(f'./pages/{key}{page_num}.html', 'w') as f:
                    f.write(template)

            print(key + str(page_num) + 'done')

def post_cmd():
    os.system('git add . ')
    os.system(f'git commit -a -m "update {strftime("%Y-%m-%d %H:%M:%S", gmtime())}"')
    os.system("git push")

category = categorize_files(directory)

write_category()

with open('index.html', 'w') as f:
    f.write(index_template(category))

# post_cmd()