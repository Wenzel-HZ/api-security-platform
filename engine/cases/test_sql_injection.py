import allure
import pytest
from utils.client import APIClient
from utils.assertions import assert_no_sql_leak

# 经典 SQL 注入 payload 列表（数据驱动）
SQL_PAYLOADS = [
    "' OR '1'='1",
    "' OR '1'='1' --",
    "'; DROP TABLE users; --",
    "' UNION SELECT null,null,null --",
    "1' AND SLEEP(3) --",
]


@allure.feature("SQL 注入")
@allure.story("查询参数注入")
class TestSQLInjection:

    @pytest.fixture(autouse=True)
    def setup(self, base_url, user_headers):
        self.client = APIClient(base_url, user_headers)

    @allure.title("GET 参数 SQL 注入 — {payload}")
    @pytest.mark.parametrize("payload", SQL_PAYLOADS)
    def test_get_param_injection(self, payload):
        """在 GET 查询参数中注入，响应体不应泄露 SQL 错误"""
        with allure.step(f"发送 payload: {payload}"):
            resp = self.client.get("/api/users", params={"id": payload})
        with allure.step("断言无 SQL 错误泄露"):
            assert resp.status_code != 500, "服务器返回 500，可能触发异常"
            assert_no_sql_leak(resp)

    @allure.title("POST Body SQL 注入")
    @pytest.mark.parametrize("payload", SQL_PAYLOADS[:3])
    def test_post_body_injection(self, payload):
        """在登录接口 POST body 注入"""
        with allure.step(f"发送登录请求，username={payload}"):
            resp = self.client.post("/api/login",
                                    json={"username": payload,
                                          "password": "anything"})
        with allure.step("断言无 SQL 错误泄露"):
            assert resp.status_code != 500
            assert_no_sql_leak(resp)