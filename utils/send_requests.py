from typing import Optional, Dict, Union
import requests


class HttpRequests:
    """
    request 二次封装，支持所有HTTP请求
    """

    def __init__(self):
        """
        初始化session请求配置,自动关联cookie
        """
        self.session = requests.Session()

    def _send_request(self,
                      method: str,
                      url: str,
                      params: Optional[Dict] = None,
                      data: Optional[Union[Dict, str]] = None,
                      json: Optional[Dict] = None,
                      **kwargs
                      ):
        """
        底层发送请求方法，统一处理异常
        """
        # 拼接完整的URL
        # full_url = self.base_url + url if self.base_url else url
        try:
            # 发送请求
            response = self.session.request(
                method=method.upper(),
                url=url,
                params=params,
                data=data,
                json=json,
                # headers=self.headers,
                # timeout=self.timeout,
                **kwargs
            )
            # 自动抛出 HTTP错误(4xx/5xx)
            response.raise_for_status()
            return response
        except requests.exceptions.Timeout:
            print("请求超时...")
            raise
        except requests.exceptions.ConnectionError:
            print("连接失败...")
            raise
        except requests.exceptions.HTTPError as err:
            print(f"HTTP 错误:{err}")
            raise

    def get(self, url, params=None, **kwargs):
        """GET 请求"""
        return self._send_request("GET", url, params, **kwargs)

    def post(self, url, json, data, **kwargs):
        """POST请求"""
        return self._send_request("POST", url, json=json, data=data, **kwargs)

    def put(self, url, json, **kwargs):
        """PUT 请求"""
        return self._send_request("PUT", url, json=json, **kwargs)

    def delete(self, url, **kwargs):
        """DELETE请求"""
        return self._send_request("DELETE", url, **kwargs)

    def get_json(self, *args, **kwargs):
        """直接返回JSON 字典, 把get请求返回的内容转换成JSON"""
        return self.get(*args, **kwargs).json()

    def post_json(self, *args, **kwargs):
        """直接返回POST请求响应的JSON"""
        return self.post(*args, **kwargs).json()
