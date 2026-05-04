import pytest
import os
from dotenv import load_dotenv

load_dotenv()

# ── 全局配置 ──────────────────────────────────────────
BASE_URL = os.getenv("TARGET_URL", "http://localhost:8080")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "eyJ_admin_token_here")
USER_TOKEN  = os.getenv("USER_TOKEN",  "eyJ_user_token_here")


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture(scope="session")
def admin_headers():
    return {"Authorization": f"Bearer {ADMIN_TOKEN}",
            "Content-Type": "application/json"}


@pytest.fixture(scope="session")
def user_headers():
    return {"Authorization": f"Bearer {USER_TOKEN}",
            "Content-Type": "application/json"}


@pytest.fixture(scope="session")
def no_auth_headers():
    return {"Content-Type": "application/json"}