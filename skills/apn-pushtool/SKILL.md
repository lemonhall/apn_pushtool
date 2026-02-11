# apn-pushtool

一个用于向 iOS 设备发送 APNs 推送的本地 CLI 工具技能（Windows 11 + PowerShell + uv）。

## Safety（必须遵守）
- 绝不把真实 `TEAM_ID` / `KEY_ID` / `DEVICE_TOKEN` / `.p8` 私钥内容写进仓库文件或日志。
- `.env` 与 `.p8` 文件必须保持本地化（已在 `.gitignore` 中忽略）。
- 如发现密钥已进入 git 历史：视为泄露，优先建议用户吊销/重签发（不要尝试“继续使用旧密钥”）。
- 任何会触发真实推送的操作（E2E）必须二次确认，并明确说明会向手机发送通知。

## Quick Commands（PowerShell）
- 安装依赖：`uv sync`
- 初始化配置：`Copy-Item .env.example .env`
- 配置诊断：`uv run apn-pushtool doctor`
- 发送单条：`uv run apn-pushtool send --title "测试" --body "Hello APNs"`
- 发送长文本：`uv run apn-pushtool send-long --title "测试" --text "长文本..."`
- 离线测试：`uv run pytest`
- E2E 真推送（需显式开启）：`$env:APNS_E2E='1' ; uv run pytest -m e2e -q`

## 配置（.env）
最小必填：
- `APNS_TEAM_ID`
- `APNS_KEY_ID`
- `APNS_BUNDLE_ID`
- `APNS_P8_PATH`（推荐）或 `APNS_P8_PRIVATE_KEY`
- `APNS_DEVICE_TOKEN`（也可以用 CLI 的 `--device-token` 传）
- `APNS_ENV`：`sandbox` 或 `production`

代理（可选）：
- `HTTP_PROXY` / `HTTPS_PROXY`（例如 `http://127.0.0.1:7897`）

## 常见工作流
1) 让用户把 `.env.example` 复制为 `.env` 并填好关键变量
2) 运行 `uv run apn-pushtool doctor` 做基础诊断
3) 运行 `uv run apn-pushtool send ...` 验证最短闭环
4) 如需验收：在用户确认后运行 E2E（会真实推送）

## 故障排查（优先级顺序）
- 先跑 `doctor`，确认环境、Bundle ID、P8 读取无误
- 检查 `APNS_ENV` 是否与 device token 来源一致（沙盒 token 不能用于生产，反之亦然）
- 如在中国大陆网络环境：确认已设置 `HTTP_PROXY` / `HTTPS_PROXY`
- 根据 APNs 返回的 `reason` 排查：`BadDeviceToken` / `InvalidProviderToken` / `TopicDisallowed`
