import allure
import pytest
import time
from utils.client import APIClient
from utils.assertions import assert_rate_limited


@allure.feature("限流")
class TestRateLimit:

    @pytest.fixture(autouse=True)
    def setup(self, base_url, user_headers):
        self.client = APIClient(base_url, user_headers)

    @allure.story("基础限流")
    @allure.title("短时间内超频请求触发 429")
    def test_burst_triggers_429(self):
        """连续发送 60 次请求，至少有一次应返回 429"""
        responses = []
        with allure.step("连续发送 60 次请求"):
            for _ in range(60):
                resp = self.client.get("/api/items")
                responses.append(resp.status_code)
                if resp.status_code == 429:
                    break  # 已触发限流，提前退出

        with allure.step("断言存在 429 响应"):
            assert 429 in responses, \
                f"60 次请求均未触发限流，状态码列表: {set(responses)}"

    @allure.story("限流绕过")
    @allure.title("伪造 X-Forwarded-For 不应绕过限流")
    def test_xff_bypass_attempt(self):
        """修改 X-Forwarded-For 不应绕过 IP 级限流"""
        statuses = []
        for i in range(60):
            spoofed_ip = f"10.0.0.{i % 255}"
            resp = self.client.get(
                "/api/items",
                headers={"X-Forwarded-For": spoofed_ip})
            statuses.append(resp.status_code)
            if resp.status_code == 429:
                break

        with allure.step("断言 XFF 伪造无法绕过限流"):
            assert 429 in statuses, \
                "XFF 伪造可能绕过了 IP 限流，需排查后端实现"

    @allure.story("限流恢复")
    @allure.title("限流窗口过后请求恢复正常")
    def test_rate_limit_recovery(self):
        """触发限流后等待窗口期，应恢复 200"""
        # 先触发限流
        for _ in range(60):
            r = self.client.get("/api/items")
            if r.status_code == 429:
                break

        with allure.step("等待 65 秒限流窗口重置"):
            time.sleep(65)

        with allure.step("再次请求，断言恢复 200"):
            resp = self.client.get("/api/items")
            assert resp.status_code == 200, \
                f"限流窗口后仍返回 {resp.status_code}，可能未正确重置"