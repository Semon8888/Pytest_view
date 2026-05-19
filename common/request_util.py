import json
import re

import requests

from common.yaml_util import read_config_file, read_extract_file


class RequestsUtil:
    session = requests.session()

    def __init__(self, first_node, second_node):
        # 读取配置文件中的基础url，用于和测试用例中的数据做拼接，组成最终的接口请求完整路径
        self.base_url = read_config_file(first_node, second_node)
        self.last_headers = {}

    # 统一替换方法，需要替换的数据有可能在url[string]、参数[字典、字典包含列表]、headers[字典]请求头中
    @staticmethod
    def replace_value(data):
        if data and isinstance(data, dict):
            str_data = json.dumps(data)
        else:
            str_data = data

        # 替换值
        pattern = r'\{\{.*?\}\}'
        old_value = re.findall(pattern, str_data)  # 获得待解析字符串列表
        if "{{" in str_data and "}}" in str_data:
            for i in range(str_data.count("{{")):
                for v in old_value:
                    str_data = str_data.replace(v, read_extract_file(v[2:-2]))

        # 替换完成后需要还原数据类型
        if data and isinstance(data, dict):
            data = json.loads(str_data)
        else:
            data = str_data
        return data

    def send_request(self, method, url, headers=None, **kwargs):
        # 处理method，使得其传入一样的str类型
        last_method = str(method).lower()
        # 处理基础路径：域名 + url
        self.base_url = self.base_url + self.replace_value(url)
        # 处理请求头
        if headers and isinstance(headers, dict):
            self.last_headers = self.replace_value(headers)

        # 处理请求数据，请求数据可能是以下类型，['params'、'data'、'json']
        for key, value in kwargs.items():
            if key in ['params', 'data', 'json']:
                kwargs[key] = self.replace_value(value)

        try:
            response = RequestsUtil.session.request(method=last_method, url=self.base_url, headers=self.last_headers,
                                                    **kwargs)
            response.raise_for_status()
            return response

        except requests.exceptions.Timeout:
            print("Request timed out")
            raise
        except requests.exceptions.ConnectionError:
            print("Connection error")
            raise
        except requests.exceptions.HTTPError as err:
            print("HTTP error {}".format(err))
            raise
