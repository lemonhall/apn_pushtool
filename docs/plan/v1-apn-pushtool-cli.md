# v1 Plan: 隐私化 + CLI 化 + 测试闭环

## Goal
交付一个不泄露 secrets 的 `apn-pushtool` CLI，并具备离线测试与可选 E2E 真推送。

## PRD Trace
- REQ-0001-001 / REQ-0001-002 / REQ-0001-003 / REQ-0001-004 / REQ-0001-005

## Scope
### 做什么
- 配置从 `config.py` 迁移为环境变量 + `.env`（可选加载）
- 代码整理为可安装包，提供 console script
- 新增 pytest 测试（默认离线），并提供 opt-in E2E（真实 APNs）
- 编写操作手册与可安装的 SKILL 文档

### 不做什么
- 不接入任何线上存储/数据库
- 不做 GUI
- 不把 Apple Developer 申请流程写成教程

## Acceptance（硬口径）
- Secrets 清零：仓库内不出现真实密钥/私钥/token（见 v1-index M1）
- CLI 可用：`apn-pushtool doctor/send/send-long` 可运行
- 默认离线全绿：`uv run pytest` 通过
- E2E opt-in：设置开关与必要 env 后，真实推送请求返回 200
- 手册与 SKILL：文件齐全，命令可复制执行

## Files（预计变更）
- 新增：`src/apn_pushtool/**`、`tests/**`、`docs/manual.md`、`skills/apn-pushtool/SKILL.md`、`.env.example`
- 修改：`pyproject.toml`、`README.md`、`.gitignore`
- 处理：`config.py`、`hello.py`、`push_tool.py`、`test_push.py`、`setup_config.py`（迁移/保留 wrapper/或弃用）

## Steps（严格顺序）

1) TDD Red：写“配置加载与校验”单元测试（应失败）
- 命令：`uv run pytest -q`
- 预期：因缺少新模块/函数而失败

2) TDD Green：实现配置模块（`.env` 可选加载 + env 校验）
- 再跑：`uv run pytest -q` → 绿

3) TDD Red：写“发送请求构造正确”的离线集成测试（MockTransport）
- 预期：当前 `APNPushTool` 不可注入 transport → 红

4) TDD Green：重构 `APNPushTool` 支持注入 transport/client，并保持对外 API 稳定

5) CLI：实现 `apn-pushtool`（doctor/send/send-long），并提供 console script
- 验证：`uv run apn-pushtool --help`

6) Secrets 清零：移除仓库内真实 key/token/private key；加入 `.env.example` + `.gitignore`
- 验证：`rg ...` 无敏感匹配

7) E2E：新增 `pytest -m e2e` 用例（默认 skip），并在手册里给出执行命令

8) 文档：更新 `README.md`（迁移到新 CLI 与 `.env`）

9) 手册与 SKILL：补 `docs/manual.md` 与 `skills/apn-pushtool/SKILL.md`

## Risks
- APNs 的 E2E 测试在网络/代理环境下易波动：必须 opt-in 且提供清晰诊断输出。

