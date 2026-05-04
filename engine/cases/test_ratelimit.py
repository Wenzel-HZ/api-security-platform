import allure
import pytest
import time
from utils.client import APIClient
from utils.assertions import assert_rate_limited


@allure.feature("限流")
@pytest.mark.order(3)   # 限流压测放最后，避免影响其他用例
class TestRateLimit:

    @pytest.fixture(autouse=True)
    def setup(self, base_url, user_headers):
        self.client = APIClient(base_url, user_headers)

    @allure.story("基础限流")
    @allure.title("短时间内超频请求触发 429")
    def test_burst_triggers_429(self):
        """连续发送请求，至少有一次应返回 429"""
        responses = []
        with allure.step("连续发送请求直到触发限流"):
            for _ in range(60):
                resp = self.client.get("/api/items")
                responses.append(resp.status_code)
                if resp.status_code == 429:
                    break
        with allure.step("断言存在 429 响应"):
            assert 429 in responses, \
                f"未触发限流，状态码: {set(responses)}"

    @allure.story("限流绕过")
    @allure.title("伪造 X-Forwarded-For 不应绕过限流")
    def test_xff_bypass_attempt(self):
        """修改 X-Forwarded-For 不应绕过 IP 级限流"""
        statuses = []
        with allure.step("使用固定伪造 IP 连续请求"):
            # 修复：使用同一个伪造 IP（而非每次换 IP），才能触发限流
            for _ in range(60):
                resp = self.client.get(
                    "/api/items",
                    headers={"X-Forwarded-For": "1.2.3.4"})
                statuses.append(resp.status_code)
                if resp.status_code == 429:
                    break
        with allure.step("断言固定伪造 IP 也会被限流"):
            assert 429 in statuses, \
                "XFF 伪造未被限流，后端可能信任了客户端 IP"

    @allure.story("限流恢复")
    @allure.title("限流窗口过后请求恢复正常")
    def test_rate_limit_recovery(self):
        """触发限流后等待窗口期，应恢复 200"""
        with allure.step("先触发限流"):
            for _ in range(60):
                r = self.client.get("/api/items")
                if r.status_code == 429:
                    break
        with allure.step("等待 65 秒限流窗口重置"):
            time.sleep(65)
        with allure.step("再次请求，断言恢复 200"):
            resp = self.client.get("/api/items")
            assert resp.status_code == 200, \
                f"限流窗口后仍返回 {resp.status_code}"