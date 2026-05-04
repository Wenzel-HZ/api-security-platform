\# API Security Audit \& Automation Platform



![CI](https://github.com/Wenzel-HZ/api-security-platform/actions/workflows/ci.yml/badge.svg)
![Security Scan](https://github.com/Wenzel-HZ/api-security-platform/actions/workflows/security-scan.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![Go](https://img.shields.io/badge/Go-1.22-00ADD8)
![License](https://img.shields.io/badge/license-MIT-green)



针对内部 API 的\*\*安全审计与自动化测试平台\*\*，覆盖 OWASP Top10 高危场景。



\## 技术栈



| 层级 | 技术 |

|------|------|

| 测试引擎 | Python 3.11 · pytest · requests · Allure |

| 后端 API | Go 1.22 · Gin · GORM · JWT |

| 数据存储 | MySQL 8.0 · Redis 7 |

| 容器化 | Docker · docker-compose · K8s |

| CI/CD | GitHub Actions · Trivy · Bandit |

| 可观测性 | Prometheus · Grafana · ELK |



\## 快速启动（P1 阶段 · 纯测试引擎）



```bash

git clone https://github.com/YOUR\_USERNAME/api-security-platform

cd api-security-platform/engine



pip install -r requirements.txt



\# 运行全部安全测试用例

pytest cases/ -v --alluredir=allure-results



\# 生成可视化报告

allure serve allure-results

```



\## 项目结构



```

api-security-platform/

├── engine/                  # Python 测试引擎（P1）

│   ├── cases/               # 安全测试用例

│   │   ├── test\_sql\_injection.py

│   │   ├── test\_xss.py

│   │   ├── test\_authz.py

│   │   └── test\_ratelimit.py

│   ├── utils/               # 工具库

│   │   ├── client.py        # requests 封装

│   │   ├── assertions.py    # 安全断言工具

│   │   └── reporter.py      # 报告生成

│   ├── conftest.py          # 全局 fixture（token/env）

│   └── requirements.txt

├── server/                  # Go 后端 API（P2）

│   ├── handler/             # Gin 路由处理

│   ├── model/               # GORM 数据模型

│   ├── middleware/          # JWT / 限流 / 日志

│   ├── main.go

│   └── go.mod

├── deploy/                  # 部署配置（P3）

│   ├── docker-compose.yml

│   ├── k8s/                 # Deployment / Service / Ingress

│   └── monitoring/          # Prometheus rules · Grafana JSON

├── .github/workflows/       # CI/CD 流水线

│   ├── ci.yml               # 测试 + Bandit SAST

│   └── security-scan.yml    # Trivy 镜像扫描

├── docs/                    # 架构图 / 系统设计文档

├── Makefile                 # 常用命令快捷入口

└── README.md

```



\## 安全测试覆盖场景



| 测试类型 | 描述 | OWASP 分类 |

|----------|------|------------|

| SQL 注入 | 检测未过滤的查询参数 | A03:2021 |

| 越权访问 | 水平 / 垂直越权检测 | A01:2021 |

| XSS | 反射型 / 存储型注入点 | A03:2021 |

| 限流绕过 | IP 轮换 / Header 伪造绕过 | A04:2021 |



\## 开发阶段



\- \[x] \*\*P1\*\* · 测试引擎 MVP（pytest + Allure + CI）

\- \[ ] \*\*P2\*\* · Go 后端 API（任务管理 + Redis 队列）

\- \[ ] \*\*P3\*\* · K8s 部署 + Prometheus + ELK

\- \[ ] \*\*P4\*\* · 压测 + Vault + Falco 运行时监控



