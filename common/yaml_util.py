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


# 读取测试用例文件
def read_testcases_file(case_path):
    with open(case_path, 'r', encoding="utf-8") as f:
        value = yaml.safe_load(f)
        return value


# 清空根目录下的extract文件内容
def clean_extract_file():
    with open(get_project_root() + 'extract.yml', "w", encoding="utf-8") as f:
        f.truncate()
