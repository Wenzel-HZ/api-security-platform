import re
from requests import Response


# ── SQL 注入特征 ────────────────────────────────────────
SQL_ERROR_PATTERNS = [
    r"sql syntax",
    r"mysql_fetch",
    r"ORA-\d{5}",
    r"pg_query\(\)",
    r"unclosed quotation",
    r"syntax error.*sql",
]


def assert_no_sql_leak(resp: Response):
    """响应体不应包含数据库错误信息"""
    body = resp.text.lower()
    for pattern in SQL_ERROR_PATTERNS:
        assert not re.search(pattern, body, re.IGNORECASE), \
            f"疑似 SQL 注入泄露: 匹配到 '{pattern}'\n响应: {resp.text[:300]}"


def assert_no_xss_reflect(resp: Response, payload: str):
    """响应体不应原样反射 XSS payload"""
    assert payload not in resp.text, \
        f"XSS payload 被直接反射!\npayload: {payload}\n响应: {resp.text[:300]}"


def assert_unauthorized(resp: Response):
    """无 token 时应返回 401"""
    assert resp.status_code == 401, \
        f"期望 401，实际 {resp.status_code}\n响应: {resp.text[:200]}"


def assert_forbidden(resp: Response):
    """越权访问应返回 403"""
    assert resp.status_code in (403, 404), \
        f"期望 403/404，实际 {resp.status_code}\n响应: {resp.text[:200]}"


def assert_rate_limited(resp: Response):
    """限流触发后应返回 429"""
    assert resp.status_code == 429, \
        f"期望 429（限流），实际 {resp.status_code}\n响应: {resp.text[:200]}"