import os

def categorize_files(directory):
    # 初始化结果字典
    series_dict = {}

    # 遍历目录中的所有文件
    for filename in os.listdir(directory):
        if filename.endswith('.jpg'):
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

directory = '../photo-data'
category = categorize_files(directory)

def img_template(file_name):
    return f"""
            <figure>
              <img src="http://photo-oss.ismy.wang/{file_name}-comp" alt="{file_name.replace('.jpg', '')}" onclick="openModal(this)" />
              <figcaption>{file_name.replace('.jpg', '')}</figcaption>
            </figure>
            """

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
                  <img src="http://photo-oss.ismy.wang/{category[key][0]}-thumb"/>
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