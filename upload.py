# -*- coding: utf-8 -*-
# flake8: noqa
from qiniu import Auth
from qiniu import BucketManager, put_file
import hashlib
import os

directory = '/Users/chenjiping/Library/Mobile Documents/com~apple~CloudDocs/export'

access_key = os.environ.get('QINIU_AK')
secret_key = os.environ.get('QINIU_SK')

print('ak: ' + str(access_key))
print('sk:' + str(secret_key))

q = Auth(access_key, secret_key)
bucket = BucketManager(q)
bucket_name = 'ismy'

def get_cloud_files_md5():
    ret, eof, info = bucket.list(bucket_name, None, None, None, None)
    mapping = {}
    for item in ret['items']:
        filename = item['key']
        md5 = item['md5']
        mapping[filename] = md5
    return mapping

def calc_file_md5(filename):
    with open(filename, 'rb') as fp:
        data = fp.read()
    return hashlib.md5(data).hexdigest()

def get_local_files():
    file_list = []

    # 遍历目录中的所有文件
    for filename in os.listdir(directory):
        if filename.endswith('.jpg') and ' ' in filename:
            file_list.append(filename)
    return file_list
            

def diff():
  cloud_files = get_cloud_files_md5()
  local_files = get_local_files()
  # 以本地文件为准
  upload_to_cloud = 0
  md5_difference = 0
  del_from_cloud = 0
  for filename in local_files:
      local_md5 = calc_file_md5(os.path.join(directory, filename))
      # 文件不在云端
      if filename not in cloud_files:
        print(filename + ' 不在云端，准备上传')
        # 上传文件
        token = q.upload_token(bucket_name, filename, 3600)
        ret, info = put_file(token, filename, os.path.join(directory, filename))
        print(ret, info)
        upload_to_cloud += 1
      elif local_md5 != cloud_files[filename]:
        print(filename + ' md5不一致，准备上传')
        # 上传文件
        token = q.upload_token(bucket_name, filename, 3600)
        ret, info = put_file(token, filename, os.path.join(directory, filename))
        print(ret, info)
        md5_difference += 1
      else:
          print(filename + ' 云端本地一致，无需上传')
  # 删除不在本地的云端文件
  for filename in cloud_files:
      if filename not in local_files:
          print(filename + ' 不在本地，准备删除')
          # 删除云端文件
          ret, info = bucket.delete(bucket_name, filename)
          print(ret, info)
          del_from_cloud += 1
  print(f'不在云端上传数 {upload_to_cloud}, md5 不一致上传数 {md5_difference}, 删除不在本地的云端文件数 {del_from_cloud}' )

diff()
