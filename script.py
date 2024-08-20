import os
from time import gmtime, strftime
from PIL import Image

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

directory = '/Users/chenjiping/Library/Mobile Documents/com~apple~CloudDocs/export'
category = categorize_files(directory)

def img_template(file_name):
    with Image.open(directory + '/' + file_name) as img:
      # 根据图片设置宽高比例，获得最好的效果
      imgSize = img.size
      width, height = imgSize[0], imgSize[1]
      if height > width:
          height = 960
          width = 540
      elif width > height:
          height = 540
          width = 960
      else:
          height = 800
          width = 800 
      return f"""
              <figure>
                <img src="https://photo-oss.ismy.wang/{file_name}-comp" alt="{file_name.replace('.jpg', '')}" width="100%" height="{height}" onclick="openModal(this)" loading="lazy" />
                <figcaption>{file_name.replace('.jpg', '')}</figcaption>
              </figure>
              """

def post_cmd():
    os.system('git add . ')
    os.system(f'git commit -a -m "update {strftime("%Y-%m-%d %H:%M:%S", gmtime())}"')
    os.system("git push")

def fill_template(name, file_list):
    with open('category_template.html', 'r') as f:
        template = f.read()
        template = template.replace('{{name}}', name)
        left = ''
        right = ''
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