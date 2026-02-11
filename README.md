# APN推送工具

基于Python的Apple Push Notification推送工具，用于向iOS设备发送推送通知。

## 使用前提（iOS 端）
要让这套推送链路真正“可用”，你需要 iPhone 上有一个**已启用 APNs 推送能力**的 App 来：
- 产生可用的 `Device Token`
- 接收你从本工具发出的推送通知

例如：你可以在 App Store 安装你使用的 iOS 应用 **“APNs Tool”**，并在其中获取 `Device Token`（以及确认对应的 `Bundle ID` / 环境为 `sandbox` 或 `production`）。

## 功能特点

- 🚀 使用Apple官方HTTP/2 APNs协议
- 🔐 支持JWT认证（基于P8私钥）
- 🏖️ 支持沙盒和生产环境
- 📱 简单易用的Python API
- 🛠️ 交互式命令行工具
- ⚡ 异步处理，高效稳定

## 快速开始

### 1. 安装依赖

```powershell
uv sync
```

### 1.5 全局安装 CLI（推荐）
安装为全局命令后，可直接运行 `apn-pushtool`（不需要 `uv run ...`）。

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

重开终端后验证：
```powershell
apn-pushtool --help
```

### 2. 配置认证信息

本项目使用环境变量（推荐配合 `.env`）注入敏感信息，避免把密钥写进仓库。

复制示例文件并填写：

```powershell
Copy-Item .env.example .env
notepad .env
```

至少需要：
- `APNS_TEAM_ID`
- `APNS_KEY_ID`
- `APNS_BUNDLE_ID`
- `APNS_P8_PATH`（推荐，指向 `.p8` 文件）或 `APNS_P8_PRIVATE_KEY`
- `APNS_DEVICE_TOKEN`（也可以在命令行传 `--device-token`）

### 3. 获取必要信息

从 iOS App **“APNs Tool”**（第二个页签 **Credentials**）或 Apple Developer 控制台获取/确认以下信息，然后填写到你的 `.env` 里：

- `APNS_TEAM_ID`（Team ID）
- `APNS_KEY_ID`（Key ID）
- `APNS_BUNDLE_ID`（Bundle ID / Topic）
- `APNS_DEVICE_TOKEN`（Device Token）
- `APNS_ENV`（sandbox/production，与 token 环境匹配）

关于 `.p8`：
- 你可以在 **“APNs Tool” → Credentials** 中直接复制 **P8 私钥内容**，保存为一个文本文件并把后缀改成 `.p8`（例如 `apns_authkey.p8`）。
- 然后在 `.env` 里填写 `APNS_P8_PATH` 指向该文件。
  - 推荐把 `.p8` 放在 `.env` 同目录下，此时可以直接写相对路径：`APNS_P8_PATH=apns_authkey.p8`（本工具会按 `.env` 所在目录解析）。
- 也可以把私钥内容直接写入 `APNS_P8_PRIVATE_KEY`（不推荐，容易多行转义出错）。

### 推荐的文件放置（SKILL + secrets）
建议把 secrets 跟随 SKILL 一起放在 `~/.agents/skills/apn-pushtool/` 下，方便在任意目录直接调用：

```text
C:\Users\<you>\.agents\skills\apn-pushtool\
├── SKILL.md
└── secrets\
    ├── .env
    └── apns_authkey.p8
```

### 4. 运行推送工具

```powershell
apn-pushtool --help
apn-pushtool doctor
apn-pushtool send --title "测试" --body "Hello APNs"
```

## 在 Codex 里用 SKILL 触发发送
如果你已经把 SKILL 安装到 `~/.agents/skills/apn-pushtool/`（见下方目录结构），在 Codex 对话里直接用技能名触发即可：

- 发送一条推送：`$apn-pushtool 给我手机发一条消息，就说该吃饭了`
- 自定义标题与内容：`$apn-pushtool 用“提醒”做标题，内容写“记得喝水”`

说明：
- 该 SKILL 会调用本机已安装的全局命令 `apn-pushtool`。
- 默认读取 `APNS_DOTENV`，若未设置则读取 `~/.agents/skills/apn-pushtool/secrets/.env`（如果存在）。

## 代码示例

### 基础用法

```python
import asyncio
from apn_pushtool.client import ApnsClient
from apn_pushtool.config import load_apns_credentials

async def send_notification():
    creds = load_apns_credentials(dotenv_path=".env")
    client = ApnsClient(creds)
    
    payload = client.create_basic_payload(title="Hello", body="这是一条推送消息", badge=1)
    
    result = await client.send_push(device_token="your_device_token", payload=payload)
    print(result)

# 运行
asyncio.run(send_notification())
```

### 高级用法

```python
# 自定义推送内容
payload = {
    "aps": {
        "alert": {
            "title": "标题",
            "body": "内容",
            "action-loc-key": "PLAY"
        },
        "badge": 1,
        "sound": "default",
        "category": "GAME_INVITATION"
    },
    "custom_data": {
        "user_id": 123,
        "action": "game_invite"
    }
}

# 发送推送
result = await push_tool.send_push(
    device_token="your_device_token",
    payload=payload,
    priority=10,
    collapse_id="game_invite"
)
```

## 环境说明

- **沙盒环境**: 用于开发和测试，只能向开发版应用发送推送
- **生产环境**: 用于正式发布的应用

通过环境变量切换：`APNS_ENV=sandbox|production`（或 `APNS_USE_SANDBOX=true|false`）。

## 错误处理

常见错误及解决方案：

| 错误代码 | 错误原因 | 解决方案 |
|---------|---------|---------|
| BadDeviceToken | Device Token无效 | 检查token格式和有效性 |
| InvalidProviderToken | 认证信息错误 | 检查Team ID、Key ID、P8私钥 |
| TopicDisallowed | Bundle ID不匹配 | 确认Bundle ID正确 |
| DeviceTokenNotForTopic | Token与应用不匹配 | 确认device token来自正确的应用 |

## 注意事项

1. **私钥安全**: 请妥善保管P8私钥文件，不要提交到版本控制系统
2. **Token有效性**: Device Token会定期更新，请确保使用最新的token
3. **环境匹配**: 沙盒环境的token不能用于生产环境，反之亦然
4. **速率限制**: Apple对推送频率有限制，避免短时间内大量推送

## 依赖说明

- `httpx[http2]`: HTTP/2客户端，用于与APNs通信
- `cryptography`: 加密库，用于处理P8私钥
- `pyjwt`: JWT库，用于生成认证token

这些都是轻量级的官方推荐库，避免了重型框架依赖。

## 故障排查

如果推送失败，请按以下步骤检查：

1. 确认iOS设备已安装对应Bundle ID的应用
2. 确认应用已获得推送权限
3. 检查网络连接是否正常
4. 验证所有配置信息是否正确
5. 查看推送返回的错误信息

## 许可证

MIT License
