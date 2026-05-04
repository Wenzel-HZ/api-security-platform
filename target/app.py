"""
Mock 靶机 — 故意包含以下漏洞供测试引擎检测：
  - SQL 注入（直接拼接 SQL 语句）
  - 反射型 / 存储型 XSS（未转义输出）
  - 水平 / 垂直越权（未校验身份）
  - 限流不足（可被 XFF 绕过）

警告：仅限本地开发环境，切勿部署到公网！
"""
from flask import Flask, request, jsonify
from collections import defaultdict
import time

app = Flask(__name__)

# ── 内存数据 ────────────────────────────────────────────
USERS = {
    "1": {"id": "1", "name": "Alice", "role": "admin",  "email": "alice@example.com"},
    "2": {"id": "2", "name": "Bob",   "role": "user",   "email": "bob@example.com"},
    "999": {"id": "999", "name": "Charlie", "role": "user", "email": "charlie@example.com"},
}
COMMENTS = {}
COMMENT_ID = [1]

TOKENS = {
    "eyJ_admin_token_here": {"user_id": "1", "role": "admin"},
    "eyJ_user_token_here":  {"user_id": "2", "role": "user"},
}

# ── 限流计数器（按真实 IP，XFF 可绕过） ────────────────────
rate_counters = defaultdict(list)
RATE_LIMIT    = 30
RATE_WINDOW   = 60


def get_client_ip():
    # 漏洞：信任客户端传来的 X-Forwarded-For，可被伪造绕过
    return request.headers.get("X-Forwarded-For", request.remote_addr)


def is_rate_limited(ip: str) -> bool:
    now   = time.time()
    hits  = rate_counters[ip]
    hits[:] = [t for t in hits if now - t < RATE_WINDOW]
    if len(hits) >= RATE_LIMIT:
        return True
    hits.append(now)
    return False


def get_current_user():
    auth = request.headers.get("Authorization", "")
    token = auth.replace("Bearer ", "").strip()
    return TOKENS.get(token)


# ══════════════════════════════════════════════════════════
# 认证 & 用户接口
# ══════════════════════════════════════════════════════════

@app.route("/api/login", methods=["POST"])
def login():
    # 漏洞：拼接 SQL 并将错误信息返回给客户端
    data     = request.get_json() or {}
    username = data.get("username", "")
    fake_sql = f"SELECT * FROM users WHERE username='{username}'"
    if any(k in username.lower() for k in ["'", "drop", "union", "sleep", "or '1"]):
        return jsonify({
            "error": f"You have an error in your SQL syntax near '{username}'",
            "query": fake_sql
        }), 500
    return jsonify({"token": "eyJ_user_token_here", "message": "ok"})


@app.route("/api/users/<user_id>")
def get_user(user_id):
    # 要求认证
    if not get_current_user():
        return jsonify({"error": "Unauthorized"}), 401
    user = USERS.get(user_id)
    if not user:
        return jsonify({"error": "Not found"}), 404
    return jsonify(user)


@app.route("/api/users/<user_id>/profile")
def get_profile(user_id):
    # 漏洞：不校验当前用户是否有权查看 user_id 的资料（水平越权）
    cur = get_current_user()
    if not cur:
        return jsonify({"error": "Unauthorized"}), 401
    user = USERS.get(user_id)
    if not user:
        return jsonify({"error": "Not found"}), 404
    return jsonify(user)   # ← 任何登录用户都能看所有人的资料


@app.route("/api/users/<user_id>/posts/<post_id>", methods=["DELETE"])
def delete_post(user_id, post_id):
    # 漏洞：不验证当前用户是否拥有该 post（水平越权）
    cur = get_current_user()
    if not cur:
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify({"deleted": post_id})   # ← 直接删除，不鉴权


@app.route("/api/admin/users")
def admin_users():
    # 漏洞：只检查 token 存在，不验证 role（垂直越权）
    cur = get_current_user()
    if not cur:
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify(list(USERS.values()))   # ← 普通用户也能访问


# ══════════════════════════════════════════════════════════
# XSS 接口
# ══════════════════════════════════════════════════════════

@app.route("/api/search")
def search():
    # 漏洞：直接把 q 参数反射回响应体，未做转义
    q = request.args.get("q", "")
    return jsonify({"query": q, "results": []})   # ← XSS payload 原样返回


@app.route("/api/comments", methods=["POST"])
def post_comment():
    data    = request.get_json() or {}
    content = data.get("content", "")
    cid     = str(COMMENT_ID[0])
    COMMENTS[cid] = content   # ← 未转义，存储型 XSS
    COMMENT_ID[0] += 1
    return jsonify({"id": cid}), 201


@app.route("/api/comments/<comment_id>")
def get_comment(comment_id):
    content = COMMENTS.get(comment_id, "")
    return jsonify({"id": comment_id, "content": content})   # ← 未转义输出


# ══════════════════════════════════════════════════════════
# 限流接口
# ══════════════════════════════════════════════════════════

@app.route("/api/items")
def get_items():
    ip = get_client_ip()   # 漏洞：信任 XFF，可伪造绕过
    if is_rate_limited(ip):
        return jsonify({"error": "Too Many Requests"}), 429
    return jsonify({"items": ["item1", "item2", "item3"]})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)