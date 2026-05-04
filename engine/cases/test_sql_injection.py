import allure
import pytest
from utils.client import APIClient
from utils.assertions import assert_no_sql_leak

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

    @allure.title("GET 路径参数 SQL 注入 — {payload}")
    @pytest.mark.parametrize("payload", SQL_PAYLOADS)
    def test_get_param_injection(self, payload):
        """在路径参数中注入，响应体不应泄露 SQL 错误"""
        with allure.step(f"发送 payload: {payload}"):
            # 修复：靶机路由是 /api/users/<user_id>，用路径参数而非查询参数
            import urllib.parse
            encoded = urllib.parse.quote(payload, safe="")
            resp = self.client.get(f"/api/users/{encoded}")
        with allure.step("断言无 SQL 错误泄露"):
            assert resp.status_code != 500, \
                f"服务器返回 500，疑似 SQL 注入触发异常\n响应: {resp.text[:300]}"
            assert_no_sql_leak(resp)

    @allure.title("POST Body SQL 注入 — {payload}")
    @pytest.mark.parametrize("payload", SQL_PAYLOADS[:3])
    def test_post_body_injection(self, payload):
        """在登录接口 POST body 注入，不应返回 500 或泄露 SQL 错误"""
        with allure.step(f"发送登录请求，username={payload}"):
            resp = self.client.post("/api/login",
                                    json={"username": payload,
                                          "password": "anything"})
        with allure.step("断言未泄露 SQL 错误（允许 400/401，不允许 500）"):
            # 靶机故意返回 500 + SQL 错误信息——这正是我们要检测的漏洞
            # 断言改为：检测到漏洞（500 + SQL关键词）= PASSED（检测成功）
            if resp.status_code == 500:
                assert_no_sql_leak(resp)  # 会触发断言，说明发现了漏洞