# v1 Index: apn_pushtool 工程化

## Vision
见 `docs/prd/PRD-0001-apn-pushtool-cli.md`

## Milestones

### M1: Secrets 清零（done = 仓库无敏感信息）
- Scope: REQ-0001-001
- DoD（硬）：
  - `.gitignore` 忽略 `.env` / `.env.*` / `*.p8`
  - 仓库内不存在 `config.py` 这类“把密钥写进代码”的配置方式（改用 `.env`/环境变量）
  - `.env.example` 仅包含占位符，不包含真实值

### M2: CLI 可用（done = 可安装+可运行）
- Scope: REQ-0001-002
- DoD（硬）：
  - `uv run apn-pushtool --help` exit code = 0
  - `uv run apn-pushtool doctor` exit code = 0（配置齐全时）

### M3: 测试闭环（done = 默认离线全绿）
- Scope: REQ-0001-003
- DoD（硬）：
  - `uv run pytest` exit code = 0
  - 测试不依赖真实 APNs；需要真实 APNs 的用例必须打 `e2e` 标记并默认 skip

### M4: E2E 推送（done = 可 opt-in 真推送）
- Scope: REQ-0001-004
- DoD（硬）：
  - `APN_E2E=1`（或等价开关）开启时，`uv run pytest -m e2e` exit code = 0，且输出包含 APNs 200 响应
  - 用户人工确认手机收到推送

### M5: 手册与 SKILL（done = 可复用）
- Scope: REQ-0001-005
- DoD（硬）：
  - `docs/manual.md` 完整，包含一条从 0 到 1 的可复制命令链
  - `skills/apn-pushtool/SKILL.md` 包含 Quick Commands + 安全边界 + 故障排查

## Plan Index
- `docs/plan/v1-apn-pushtool-cli.md`

## Traceability Matrix（最小版）
| Req ID | PRD | v1 Plan | Tests/Commands | Evidence |
|---|---|---|---|---|
| REQ-0001-001 | PRD-0001 | v1-apn-pushtool-cli | `rg ...` / `.gitignore` | 本地命令输出 |
| REQ-0001-002 | PRD-0001 | v1-apn-pushtool-cli | `uv run apn-pushtool --help` | 本地命令输出 |
| REQ-0001-003 | PRD-0001 | v1-apn-pushtool-cli | `uv run pytest` | 本地命令输出 |
| REQ-0001-004 | PRD-0001 | v1-apn-pushtool-cli | `uv run pytest -m e2e` | 本地命令输出 + 手机人工确认 |
| REQ-0001-005 | PRD-0001 | v1-apn-pushtool-cli | 打开文档/skill | 文件存在 |

## ECN Index
（v1 暂无）

## Differences（v1 结束后填写）
（待完成后回填）
