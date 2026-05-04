import allure
import pytest
from utils.client import APIClient
from utils.assertions import assert_unauthorized, assert_forbidden


@allure.feature("越权访问")
class TestAuthorization:

    @pytest.fixture(autouse=True)
    def setup(self, base_url, admin_headers, user_headers, no_auth_headers):
        self.admin  = APIClient(base_url, admin_headers)
        self.user   = APIClient(base_url, user_headers)
        self.no_auth = APIClient(base_url, no_auth_headers)

    # ── 未认证访问 ─────────────────────────────────────────
    @allure.story("未认证访问")
    @allure.title("无 token 访问受保护资源 → 401")
    def test_no_token_returns_401(self):
        resp = self.no_auth.get("/api/users/1")
        assert_unauthorized(resp)

    # ── 水平越权：普通用户访问他人数据 ───────────────────────
    @allure.story("水平越权")
    @allure.title("user 访问其他用户的私有资源 → 403/404")
    def test_horizontal_privilege_escalation(self):
        """user token 不应能读取 user_id=999（他人数据）"""
        resp = self.user.get("/api/users/999/profile")
        assert_forbidden(resp)

    # ── 垂直越权：普通用户访问管理员接口 ─────────────────────
    @allure.story("垂直越权")
    @allure.title("普通用户调用管理员接口 → 403")
    def test_vertical_privilege_escalation(self):
        """普通用户不能访问 /api/admin/ 下的接口"""
        resp = self.user.get("/api/admin/users")
        assert_forbidden(resp)

    @allure.title("普通用户尝试删除他人资源 → 403")
    def test_delete_other_user_resource(self):
        resp = self.user.delete("/api/users/999/posts/1")
        assert_forbidden(resp)

    # ── 管理员接口正常可用（正向验证）─────────────────────────
    @allure.story("正向验证")
    @allure.title("admin token 访问管理员接口 → 200")
    def test_admin_can_access_admin_api(self):
        resp = self.admin.get("/api/admin/users")
        assert resp.status_code == 200, \
            f"admin 应能访问管理接口，实际 {resp.status_code}"