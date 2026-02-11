# 操作手册：apn-pushtool（Windows 11 + PowerShell + uv）

## 0. 前置条件
- 已安装 `uv`
- 有可用的 APNs Auth Key（`.p8`）、Team ID、Key ID、App 的 Bundle ID
- 有目标设备的 `Device Token`（64 位 hex）

## 1. 安装依赖
```powershell
uv sync
```

## 2. 配置（推荐用 .p8 路径）
```powershell
Copy-Item .env.example .env
notepad .env
```

至少填写这些变量：
- `APNS_TEAM_ID`
- `APNS_KEY_ID`
- `APNS_BUNDLE_ID`
- `APNS_P8_PATH`（推荐）或 `APNS_P8_PRIVATE_KEY`
- `APNS_DEVICE_TOKEN`（也可以运行时用 `--device-token` 传）
- `APNS_ENV`：`sandbox` 或 `production`

## 3. 配置诊断（不打印私钥全文）
```powershell
uv run apn-pushtool doctor
```

## 4. 发送一条推送
```powershell
uv run apn-pushtool send --title "测试推送" --body "Hello APNs"
```

指定 token（不使用 `APNS_DEVICE_TOKEN`）：
```powershell
uv run apn-pushtool send --title "测试推送" --body "Hello APNs" --device-token "<64-hex-token>"
```

## 5. 发送长文本（自动切分 + 倒序发送）
```powershell
uv run apn-pushtool send-long --title "长消息" --text "这里是一段很长很长的文本..."
```

或从文件读取：
```powershell
uv run apn-pushtool send-long --title "长消息" --text-file .\\test.txt
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
