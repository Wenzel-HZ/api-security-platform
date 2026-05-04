import requests
from typing import Optional


class APIClient:
    """轻量封装，统一管理请求 / 超时 / 错误日志"""

    def __init__(self, base_url: str, headers: Optional[dict] = None,
                 timeout: int = 10):
        self.base_url = base_url.rstrip("/")
        self.session  = requests.Session()
        if headers:
            self.session.headers.update(headers)
        self.timeout = timeout

    def get(self, path: str, **kwargs):
        return self.session.get(
            f"{self.base_url}{path}", timeout=self.timeout, **kwargs)

    def post(self, path: str, **kwargs):
        return self.session.post(
            f"{self.base_url}{path}", timeout=self.timeout, **kwargs)

    def put(self, path: str, **kwargs):
        return self.session.put(
            f"{self.base_url}{path}", timeout=self.timeout, **kwargs)

    def delete(self, path: str, **kwargs):
        return self.session.delete(
            f"{self.base_url}{path}", timeout=self.timeout, **kwargs)