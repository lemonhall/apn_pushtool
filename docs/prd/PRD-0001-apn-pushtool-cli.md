# PRD-0001: APN PushTool 隐私化 + CLI 工程化

## Vision
把当前的 APNs 推送脚本整理为一个“可安装、可配置、可验证”的 CLI 工具：
- **隐私安全**：仓库内不出现任何真实密钥/Token/私钥；配置通过 `.env`/环境变量注入，默认不泄露。
- **工程化**：有清晰的包结构、可重复的命令、可跑的自动化测试（离线为主）。
- **可验收**：提供一条可重复执行的 E2E 命令链路，能真实调用 APNs 并成功推送到手机（以 APNs 200 响应为硬证据，手机收到通知为人工确认）。
- **可复用**：附操作手册，并产出一个可安装的 Codex SKILL。

## Non-Goals
- 不做 GUI。
- 不做多租户/多账号管理（先聚焦单个开发者本地使用）。
- 不做 Apple Developer 账号/证书申请教学（只提供配置入口与校验）。

## Requirements

### REQ-0001-001：配置 .env 化（仓库内无 secrets）
**验收：**
- 仓库中不存在真实的 `TEAM_ID` / `KEY_ID` / `DEVICE_TOKEN` / `P8_PRIVATE_KEY` 文本。
- 默认 `.gitignore` 忽略 `.env` / `*.p8` 等敏感文件。
- 提供 `.env.example`（仅变量名与示例占位符）。
- CLI 从环境变量（以及可选 `.env`）读取配置并能运行。

### REQ-0001-002：提供正式 CLI 入口（可安装/可运行）
**验收：**
- `pyproject.toml` 定义 console script：`apn-pushtool`。
- `apn-pushtool --help` 可用，包含至少以下子命令：
  - `doctor`：打印并校验当前配置（不输出私钥全文）。
  - `send`：发送单条推送。
  - `send-long`：长文本切分为多条推送并倒序发送。

### REQ-0001-003：离线测试可跑（默认不发真实推送）
**验收：**
- `uv run pytest` 全绿（默认不触网、不发推送）。
- 单元测试覆盖：
  - `.env`/环境变量加载与校验逻辑
  - payload 生成逻辑
  - device token 清洗/校验逻辑
- 离线集成测试：通过 `httpx.MockTransport` 模拟 APNs 返回，断言请求头/URL/状态处理正确。

### REQ-0001-004：E2E 推送（真实调用 APNs）
**验收：**
- 提供 `uv run pytest -m e2e` 或等价命令，可在用户显式开启的前提下触发真实推送。
- E2E 通过的硬证据：APNs 返回 200。
- E2E 人工确认：手机收到推送通知（由用户确认）。
- 未提供必要环境变量时，E2E 测试自动跳过（不失败）。

### REQ-0001-005：操作手册与 SKILL
**验收：**
- `docs/manual.md`：从零到发出一条推送的操作流程（PowerShell/uv）。
- `skills/apn-pushtool/SKILL.md`：面向 Codex 的可执行指令（含安全约束、常用命令、故障排查）。

## Risks
- APNs 真实推送依赖网络与 Apple 服务可用性；E2E 测试必须是 opt-in（显式开关）。
- 代理环境（中国大陆）可能导致连接失败；需要在手册/doctor 中给出诊断信息与配置方式。

