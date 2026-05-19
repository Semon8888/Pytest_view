import os

import yaml


# 获取文件路径
def get_project_root():
    return os.path.abspath(os.path.dirname(__file__)).split("common")[0]


# 读取根目录下的config文件
def read_config_file(first_node, second_node):
    with open(get_project_root() + 'config.yml', "r", encoding="utf-8") as f:
        value = yaml.safe_load(f)

        return value[first_node][second_node]


# 读取根目录下的extract文件
def read_extract_file(node_name):
    with open(get_project_root() + 'extract.yml', "r", encoding="utf-8") as f:
        value = yaml.safe_load(f)

        return value[node_name]


# 写入内容到根目录下的extract文件
def write_extract_file(data):
    with open(get_project_root() + 'extract.yml', "a", encoding="utf-8") as f:
        yaml.dump(data, stream=f, allow_unicode=True)


# 清空根目录下的extract文件内容
def clean_extract_file():
    with open(get_project_root() + 'extract.yml', "w", encoding="utf-8") as f:
        f.truncate()


if __name__ == '__main__':
    file_data = {"access_token": "asd6f1as3f1as3df4a64f6asf16asdf"}
    write_extract_file(file_data)
