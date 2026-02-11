# Agent Notes (apn_pushtool)

## 项目概览
这是一个基于 Python 的 Apple Push Notification (APNs) 推送工具，提供：
- 核心库：`hello.py` 中的 `APNPushTool`（JWT 认证 + HTTP/2 调用 APNs）
- CLI：`push_tool.py`（交互式推送）、`test_push.py`（自动测试推送）、`setup_config.py`（生成本地配置）

## Quick Commands（PowerShell）
- 安装依赖（推荐）：`uv sync`
- 配置（首次）：`Copy-Item .env.example .env`
- 全局安装 CLI（一次性）：`uv tool install -e . ; uv tool update-shell`
- 配置诊断：`apn-pushtool doctor`
- 发送单条推送：`apn-pushtool send --title "测试" --body "Hello APNs"`
- 发送长文本：`apn-pushtool send-long --title "测试" --text "长文本..."`

## 语言与代码风格
- Python：`>=3.13`（见 `pyproject.toml` 与 `.python-version`）
- 保持现有风格：显式类型标注（`typing`）、异常信息可读、异步 API 用 `async/await`
- 新增依赖用 `uv add <pkg>`，并同步更新 `uv.lock`；不要手改 `uv.lock`

## 目录与入口
- 配置：`.env`（本地文件，gitignore）
- CLI：`src/apn_pushtool/cli.py`
- 核心实现：`src/apn_pushtool/client.py`
- 配置加载：`src/apn_pushtool/config.py`
- 测试：`tests/**`（默认离线，E2E 需显式开启）

## 本地环境约定（Windows 11 + PowerShell）
- 默认用 PowerShell 命令风格；连续执行命令用 `;` 分隔（不要假设 `&&` / `||` 可用）。
- `curl` / `wget` 在 PowerShell 里可能是别名；需要调用真实二进制时用 `curl.exe` / `wget.exe`。
- 需要 bash/WSL 命令时：`wsl -e bash -lc '...'`，其余保持 PowerShell。

## 配置与密钥安全（必须遵守）
- **禁止**把真实的 `TEAM_ID` / `KEY_ID` / `DEVICE_TOKEN` / `P8_PRIVATE_KEY` 提交到 git 历史。
  - 如果误提交过：视为泄露，优先在 Apple Developer 后台**吊销/重签发**密钥并清理历史（必要时重写历史）。
- 本项目目前使用 `config.py` 读取配置；任何改动如涉及配置结构，需同时更新：
  - `README.md` 的配置说明
  - `setup_config.py` 的生成逻辑

## 代理（中国大陆网络环境常用）
本地代理示例：`127.0.0.1:7897`

- 当前会话临时生效：
  - `$env:HTTP_PROXY='http://127.0.0.1:7897'`
  - `$env:HTTPS_PROXY='http://127.0.0.1:7897'`
- `git` 仅对当前仓库生效：
  - `git config --local http.proxy http://127.0.0.1:7897`
  - `git config --local https.proxy http://127.0.0.1:7897`

## 测试策略
- `test_push.py` 属于**集成测试/手动验收脚本**：需要真实 APNs 证书/设备 token，且会产生真实推送。
- 若修改 `hello.py` 的网络行为，优先补充**离线单元测试**（建议用 `httpx.MockTransport` 模拟 APNs 返回），避免 CI/本地误发推送。

## 变更边界与危险操作
- 不要在未确认的情况下执行批量删除（如 `Remove-Item -Recurse -Force` / `rm -rf`）。
- 任何可能触发“生产环境推送”的改动（例如默认 `USE_SANDBOX=False`、自动发送、批量发送）必须在 PR/提交说明中明确标注，并提示使用者二次确认。

## 多份 AGENTS.md 的覆盖规则
- 根目录 `AGENTS.md`：默认适用全仓库。
- 子目录出现 `AGENTS.md` / `AGENTS.override.md` 时：以**更具体、更靠近文件**的规则为准；同目录下 `AGENTS.override.md` 优先生效。
