# 操作手册：apn-pushtool（Windows 11 + PowerShell + uv）

## 0. 前置条件
- 已安装 `uv`
- 有可用的 APNs Auth Key（`.p8`）、Team ID、Key ID、App 的 Bundle ID
- 有目标设备的 `Device Token`（64 位 hex）

## 1. 安装依赖
```powershell
uv sync
```

## 1.5 全局安装 CLI（推荐）
把工具安装成全局命令后，就可以在任意目录直接运行 `apn-pushtool`（不需要 `uv run ...`）。

本地仓库（开发/可编辑）：
```powershell
uv tool install -e .
uv tool update-shell
```

新机器一键安装（从 GitHub）：
```powershell
uv tool install git+https://github.com/lemonhall/apn_pushtool
uv tool update-shell
```

执行 `uv tool update-shell` 后建议重开终端，然后验证：
```powershell
apn-pushtool --help
```

## 1.6 安装本技能到 `~/.agents/skills`（可选）
如果你希望 Codex/agents 能直接发现该 SKILL，可以把仓库内的 skill 安装到你的全局 skills 目录。

方式 A（PowerShell 脚本，拷贝到 `$HOME\\.agents\\skills`）：
```powershell
pwsh -File .\\scripts\\install-skill.ps1
```

方式 B（如果你已安装 `skills` CLI）：
```powershell
npx skills add lemonhall/apn_pushtool --skill apn-pushtool -g --agent codex
```

## 2. 配置（推荐用 .p8 路径）
```powershell
Copy-Item .env.example .env
notepad .env
```

如果你是从旧版脚本迁移过来，且仓库里还保留了 `__pycache__\\config*.pyc`，可以一键恢复：
```powershell
uv run apn-pushtool init-from-legacy --force
```

至少填写这些变量：
- `APNS_TEAM_ID`
- `APNS_KEY_ID`
- `APNS_BUNDLE_ID`
- `APNS_P8_PATH`（推荐）或 `APNS_P8_PRIVATE_KEY`
- `APNS_DEVICE_TOKEN`（也可以运行时用 `--device-token` 传）
- `APNS_ENV`：`sandbox` 或 `production`

### `.p8` 文件的获取方式（APNs Tool）
在 **“APNs Tool” → Credentials** 里复制 P8 私钥内容，保存为文本文件并把后缀改成 `.p8`（例如 `apns_authkey.p8`），然后在 `.env` 中设置：
- `APNS_P8_PATH=apns_authkey.p8`

如果 `.p8` 与 `.env` 在同一目录，`APNS_P8_PATH` 可以用相对路径；本工具会按 `.env` 所在目录解析。

### 推荐放置 secrets 的位置（便于跨目录调用）
如果你希望“全局安装 CLI + 全局 SKILL”后在任意目录直接用，推荐把 secrets 放在：
- `.env`：`$HOME\\.agents\\skills\\apn-pushtool\\secrets\\.env`
- `.p8`：`$HOME\\.agents\\skills\\apn-pushtool\\secrets\\apns_authkey.p8`

然后在该 `.env` 里把 `APNS_P8_PATH` 指向上面的 `.p8` 路径。

CLI 会自动优先读取 `APNS_DOTENV`，若未设置则会尝试读取上述 skill-local `.env`。

## 3. 配置诊断（不打印私钥全文）
```powershell
apn-pushtool doctor
```

## 4. 发送一条推送
```powershell
apn-pushtool send --title "测试推送" --body "Hello APNs"
```

指定 token（不使用 `APNS_DEVICE_TOKEN`）：
```powershell
apn-pushtool send --title "测试推送" --body "Hello APNs" --device-token "<64-hex-token>"
```

## 5. 发送长文本（自动切分 + 倒序发送）
```powershell
apn-pushtool send-long --title "长消息" --text "这里是一段很长很长的文本..."
```

或从文件读取：
```powershell
apn-pushtool send-long --title "长消息" --text-file .\\test.txt
```

## 6. 运行测试
默认离线测试（不触网、不发推送）：
```powershell
uv run pytest
```

## 7. E2E（真实推送到手机，需显式开启）
此步骤会真实调用 APNs，并向你的手机发送推送。

```powershell
$env:APNS_E2E='1'
uv run pytest -m e2e -q
```

验收口径：
- 自动化硬证据：测试断言 APNs 返回 HTTP 200
- 人工确认：手机实际收到通知

## 8. 常见问题

### 8.1 代理/网络问题（中国大陆）
如果你需要本地代理（如 `127.0.0.1:7897`），可以在 PowerShell 会话里设置：
```powershell
$env:HTTP_PROXY='http://127.0.0.1:7897'
$env:HTTPS_PROXY='http://127.0.0.1:7897'
```

### 8.2 常见 APNs 错误
- `BadDeviceToken`：token 格式或来源不匹配（沙盒/生产、Bundle ID、App 安装情况）
- `InvalidProviderToken`：Team/Key/P8 不匹配，或 JWT 生成失败
- `TopicDisallowed`：Bundle ID（topic）不正确或权限不足

## 9. 安全提醒（强制）
- `.env` / `.p8` 文件不要提交到 git。
- 如果任何密钥曾经进入过 git 历史或被分享到公网：视为泄露，优先在 Apple Developer 后台吊销并重签发。
