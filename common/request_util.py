import json
import re

import jsonpath
import requests

from common.yaml_util import read_config_file, read_extract_file, write_extract_file
from debug_talk import DebugTalk


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

    # 替换热加载动态变量
    @staticmethod
    def replace_hot_load(data):
        if data and isinstance(data, dict):
            str_data = json.dumps(data)
        else:
            str_data = data
            # 判断data中有几个需要进行处理的${}内容，然后逐个处理
        for times in range(1, str_data.count("${") + 1):
            if "${" in str_data and "}" in str_data:
                start_index = str_data.index("${")
                end_index = str_data.index("}")
                old_value = str_data[start_index:end_index + 1]
                # print(old_value)
                # 获得替换后的新值
                # 1、取得函数名称, 如果有待替换的有参数,那么用例文件中必然是'${}()'类型表示, 如果无参数,那么则是'${}'表示
                if '(' in str_data and ')' in str_data:
                    func_name = old_value[2:old_value.index("(")]
                    # print(func_name)
                    args_value = old_value[old_value.index("(") + 1: old_value.index(")")]
                    new_value = getattr(DebugTalk, func_name)(*args_value.split(","))
                # 2、如果无参, 则方法名就是被${}包裹的
                else:
                    func_name = old_value[2:-1]
                    # print(func_name)
                    new_value = getattr(DebugTalk, func_name)()

                str_data = str_data.replace(old_value, str(new_value))
        # 替换完成后需要还原数据类型
        if data and isinstance(data, dict):
            data = json.loads(str_data)
        else:
            data = str_data
        return data

    # 分析测试用例文件内容是否符合框架规则
    def analysis_yaml(self, case_info):
        # 1、框架规则规定, 测试用例yaml文件中, key必须包含"name", "base_url", "request", "validate"
        require_keys = ['name', 'base_url', 'request', 'validate']
        if set(require_keys).issubset(case_info.keys()):
            # 2、在request一级关键字下必须包含"method"和"url"
            request_keys = case_info['request'].keys()
            if 'method' in request_keys and 'url' in request_keys:
                method = case_info['request']['method']
                del case_info['request']['method']

                url = case_info['request']['url']
                del case_info['request']['url']
                headers = None

                if jsonpath.jsonpath(case_info, '$..headers'):
                    headers = case_info['request']['headers']
                    # 此处因为要构造发送请求函数中的**kwargs可变参数,所以用完后要删除掉,不然就会进入到可变参数中
                    del case_info['request']['headers']

                files = None
                if jsonpath.jsonpath(case_info, '$..files'):
                    files = case_info['request']['files']  # 此处返回一个字典
                    for key, value in case_info['files'].items():  # 此处通过key, value 遍历字典, 把文件打开后重新赋值给key
                        files[key] = open(value, "rb")
                    files = open(case_info['request']['files'], 'rb')
                    # 此处因为要构造发送请求函数中的**kwargs可变参数,所以用完后要删除掉,不然就会进入到可变参数中
                    del case_info['request']['files']

                # 在最后发送请求之前,应该要把method, url, headers, files 这四个数据去掉之后, 把剩下的传给可变参数**kwargs
                response = self.send_request(method=method, url=url, headers=headers, files=files,
                                             **case_info['request'])
                response_data = response.json()
                # 如果处理登录或者其他有接口关联的用例, 需要把关联数据写入extract.yml文件中
                # 提取接口关联的变量, 既要支持正则提取,又要支持json提取
                if 'extract' in case_info.keys():
                    for key, value in case_info['extract'].items():
                        # 如果测试用例文件关于数据关联使用的正则提取, 那么有如下
                        if '(.+?)' in value or '(.*?)' in value:
                            re_value = re.search(value, response.text)
                            if re_value:
                                extract_data = {key: re_value.group(1)}
                                write_extract_file(extract_data)
                            else:
                                print("没有匹配到值")
                        else:  # 否则使用json提取
                            # 把用例里面的extract关键字的key 和 请求相应内容中根据value取到的值组装成字典
                            extract_data = {key: response_data[value]}
                            # 数据关联字典写进extract.yml文件中
                            write_extract_file(extract_data)

                return response
            else:
                print("缺失二级关键字'method'和'url'")
                return None
        else:
            print("测试用例中一级关键字不全")
            raise

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
                # 1、先处理测试用例文件中postman类型的"{{}}", 处理完成之后赋值给value继续处理
                value = self.replace_value(value)
                # 2、第一步处理完后再处理"${}"或者"${}()"类型, 最后赋值给value替换成最后的请求value
                kwargs[key] = self.replace_hot_load(value)
        try:
            response = RequestsUtil.session.request(method=last_method, url=self.base_url, headers=self.last_headers,
                                                    **kwargs)
            response.raise_for_status()
            # 此处需要加入断言判断
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

    def validate_result(self, expect_result, actual_result):
        pass

# if __name__ == '__main__':
#     dic_data = {"tag": {"id": 108, "name": "semon_industry ${get_randint_num(100, 999)}"}}
#     # dic_data = {"tag": {"id": 108, "name": "semon_industry ${say_hello}"}}
#     result = RequestsUtil.replace_hot_load(dic_data)
#     print(result)
