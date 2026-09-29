# CLIProxyAPI 快速使用指南

本文档提供完整的配置和使用步骤，帮助你快速将 ChatGPT Plus 订阅转换为 API 访问。

---

## 📋 目录

1. [环境准备](#环境准备)
2. [网络配置](#网络配置)
3. [认证配置（ChatGPT Plus 转 API）](#认证配置chatgpt-plus-转-api)
4. [启动服务](#启动服务)
5. [API 使用示例](#api-使用示例)
6. [常见问题](#常见问题)

---

## 环境准备

### 系统要求
- Go 1.26+
- Linux/macOS/Windows

### 项目目录
```bash
cd /path/to/CLIProxyAPI
```

### 可执行文件
项目已编译，可执行文件：`./cli-proxy-api`

---

## 网络配置

### 配置代理（如需要）

编辑 `config.yaml` 文件，找到 `proxy-url` 配置项：

```yaml
# 第 21 行左右
proxy-url: "http://your-proxy-host:port"
```

或者通过环境变量配置：

```bash
export https_proxy=http://your-proxy-host:port
export http_proxy=http://your-proxy-host:port
export HTTPS_PROXY=http://your-proxy-host:port
export HTTP_PROXY=http://your-proxy-host:port
```

---

## 认证配置（ChatGPT Plus 转 API）

### 方法 1: 设备码认证（推荐）⭐

这是**最简单、最可靠**的方式，项目官方推荐。

#### 步骤：

1. **启动设备码认证**

```bash
cd /path/to/CLIProxyAPI

# 如果需要代理
export https_proxy=http://your-proxy-host:port
export http_proxy=http://your-proxy-host:port

# 启动认证
./cli-proxy-api -codex-device-login
```

2. **获取设备码**

程序会输出类似内容：
```
Starting Codex device authentication...
Codex device URL: https://auth.openai.com/codex/device
Codex device code: 3UEG-T1JNI
```

3. **浏览器授权**

- 在浏览器中访问：https://auth.openai.com/codex/device
- 输入设备码（例如：`3UEG-T1JNI`）
- 使用你的 ChatGPT Plus 账号登录并授权

4. **等待完成**

授权完成后，程序会自动保存认证信息：
```
Codex authentication successful
Saving credentials to ~/.cli-proxy-api/codex-xxxxxx-your-email@example.com-plus.json
Authentication saved!
Codex device authentication successful!
```

### 方法 2: OAuth 浏览器登录

适合有图形界面或 SSH 隧道的环境。

```bash
# 无浏览器模式（获取 URL）
./cli-proxy-api -codex-login --no-browser

# 然后访问输出的 URL 完成授权
```

### 方法 3: 手动 Access Token（不推荐）

此方法可能遇到 Cloudflare 防护问题，不建议使用。

1. 在浏览器中访问 https://chatgpt.com
2. 按 F12 打开开发者工具
3. 在控制台执行：
```javascript
fetch('https://chatgpt.com/api/auth/session')
  .then(r=>r.json())
  .then(d=>console.log('Access Token:\n'+d.accessToken))
```

4. 创建认证文件：
```bash
mkdir -p ~/.cli-proxy-api

cat > ~/.cli-proxy-api/codex_your-email@example.com.json <<'EOF'
{
  "type": "codex",
  "email": "your-email@example.com",
  "access_token": "eyJhbGci..."
}
EOF
```

---

## 启动服务

### 前台启动（开发测试）

```bash
cd /path/to/CLIProxyAPI
./cli-proxy-api
```

按 `Ctrl+C` 停止服务。

### 后台启动（推荐生产使用）

```bash
cd /path/to/CLIProxyAPI
nohup ./cli-proxy-api > cliproxyapi.log 2>&1 &
```

### 服务管理

**查看进程状态：**
```bash
ps aux | grep cli-proxy-api | grep -v grep
```

**查看日志：**
```bash
tail -f cliproxyapi.log
```

**停止服务：**
```bash
pkill -f cli-proxy-api
```

---

## API 使用示例

### 服务信息
- **地址**: `http://127.0.0.1:6000`
- **API Key**: `sk-cliproxyapi-test-key-001` （配置在 `config.yaml` 第 39-40 行）

### 1. 健康检查

```bash
curl http://127.0.0.1:6000/healthz
```

**响应：**
```json
{"status":"ok"}
```

### 2. 获取模型列表

```bash
curl -H "Authorization: Bearer sk-cliproxyapi-test-key-001" \
  http://127.0.0.1:6000/v1/models
```

**响应：**
```json
{
  "data": [
    {"id": "gpt-5.5", "object": "model", "owned_by": "openai"},
    {"id": "gpt-5.6-terra", "object": "model", "owned_by": "openai"},
    {"id": "gpt-5.6-luna", "object": "model", "owned_by": "openai"},
    {"id": "gpt-5.6-sol", "object": "model", "owned_by": "openai"},
    {"id": "gpt-6-astra", "object": "model", "owned_by": "openai"},
    {"id": "gpt-6-sol", "object": "model", "owned_by": "openai"},
    {"id": "codex-auto-review", "object": "model", "owned_by": "openai"},
    {"id": "gpt-image-1.5", "object": "model", "owned_by": "openai"},
    {"id": "gpt-image-2", "object": "model", "owned_by": "openai"},
    {"id": "gpt-image-2.5", "object": "model", "owned_by": "openai"},
    {"id": "gpt-image-2.5-flare", "object": "model", "owned_by": "openai"}
  ],
  "object": "list"
}
```

### 3. 聊天补全（非流式）

```bash
curl -X POST http://127.0.0.1:6000/v1/chat/completions \
  -H "Authorization: Bearer sk-cliproxyapi-test-key-001" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-5.5",
    "messages": [
      {"role": "user", "content": "你好，请用中文回答"}
    ],
    "max_tokens": 100
  }'
```

**响应：**
```json
{
  "id": "resp_...",
  "object": "chat.completion",
  "created": 1790650240,
  "model": "gpt-5.5",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "你好！很高兴见到你。我是 ChatGPT，一个 AI 助手。有什么我可以帮助你的吗？"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "completion_tokens": 25,
    "total_tokens": 331,
    "prompt_tokens": 306
  }
}
```

### 4. 聊天补全（流式）

```bash
curl -X POST http://127.0.0.1:6000/v1/chat/completions \
  -H "Authorization: Bearer sk-cliproxyapi-test-key-001" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-5.5",
    "messages": [
      {"role": "user", "content": "讲一个笑话"}
    ],
    "stream": true
  }'
```

**响应：**
```
data: {"id":"resp_...","object":"chat.completion.chunk","created":1790650255,"model":"gpt-5.5","choices":[{"index":0,"delta":{"role":"assistant","content":"好"},"finish_reason":null}]}

data: {"id":"resp_...","object":"chat.completion.chunk","created":1790650255,"model":"gpt-5.5","choices":[{"index":0,"delta":{"content":"的"},"finish_reason":null}]}

...

data: [DONE]
```

### 5. Python 调用示例

```python
import openai

# 配置 API
openai.api_key = "sk-cliproxyapi-test-key-001"
openai.api_base = "http://127.0.0.1:6000/v1"

# 聊天补全
response = openai.ChatCompletion.create(
    model="gpt-5.5",
    messages=[
        {"role": "user", "content": "你好"}
    ]
)

print(response.choices[0].message.content)
```

### 6. Node.js 调用示例

```javascript
const OpenAI = require('openai');

const openai = new OpenAI({
  apiKey: 'sk-cliproxyapi-test-key-001',
  baseURL: 'http://127.0.0.1:6000/v1',
});

async function main() {
  const completion = await openai.chat.completions.create({
    model: 'gpt-5.5',
    messages: [{ role: 'user', content: '你好' }],
  });

  console.log(completion.choices[0].message.content);
}

main();
```

---

## 常见问题

### Q1: 认证失败怎么办？

**A:** 
- 确保使用设备码认证（推荐）
- 检查网络连接和代理配置
- 确保设备码在有效期内（通常 5-10 分钟）
- 重新生成设备码重试

### Q2: 401 Unauthorized 错误？

**A:** 
- 检查认证文件是否存在：`ls ~/.cli-proxy-api/*.json`
- 使用设备码重新认证：`./cli-proxy-api -codex-device-login`
- 检查服务日志：`tail -f cliproxyapi.log`

### Q3: 如何添加多个 API Key？

**A:** 
编辑 `config.yaml` 文件：
```yaml
api-keys:
  - "sk-cliproxyapi-test-key-001"
  - "sk-cliproxyapi-test-key-002"
  - "sk-your-custom-key-003"
```

### Q4: 如何修改服务端口？

**A:** 
编辑 `config.yaml` 文件：
```yaml
host: "127.0.0.1"
port: 6000  # 修改为你想要的端口
```

### Q5: 如何查看可用模型？

**A:** 
```bash
curl -H "Authorization: Bearer sk-cliproxyapi-test-key-001" \
  http://127.0.0.1:6000/v1/models | jq '.data[].id'
```

输出：
```
"gpt-5.5"
"gpt-5.6-terra"
"gpt-5.6-luna"
"gpt-5.6-sol"
"gpt-6-astra"
"gpt-6-sol"
"codex-auto-review"
"gpt-image-1.5"
"gpt-image-2"
"gpt-image-2.5"
"gpt-image-2.5-flare"
```

### Q6: 支持哪些 API 接口？

**A:** 

| 接口 | 方法 | 功能 |
|------|------|------|
| `/healthz` | GET | 健康检查 |
| `/v1/models` | GET | 模型列表 |
| `/v1/chat/completions` | POST | 聊天补全（流式/非流式） |
| `/v1/completions` | POST | 文本补全 |
| `/v1/images/generations` | POST | 图像生成 |
| `/v1/messages` | POST | Claude 消息 |
| `/v1/responses` | POST/GET | 响应接口 |
| `/v1beta/interactions` | POST | Gemini 交互 |
| `/v1/realtime` | POST | 实时通信 |

### Q7: 认证文件保存在哪里？

**A:** 
```bash
~/.cli-proxy-api/

# 设备码认证生成的文件格式：
codex-<id>-<email>-plus.json

# 例如：
codex-xxxxxx-your-email@example.com-plus.json
```

### Q8: 如何更新认证？

**A:** 
只需重新运行设备码认证，新的认证会自动保存：
```bash
./cli-proxy-api -codex-device-login
```

### Q9: 服务启动后无法访问？

**A:** 
- 检查端口是否被占用：`netstat -tuln | grep 6000`
- 检查防火墙规则
- 确认服务正在运行：`ps aux | grep cli-proxy-api`
- 查看启动日志：`tail -f cliproxyapi.log`

### Q10: 如何验证 ChatGPT Plus 转 API 是否成功？

**A:** 
运行快速测试：
```bash
# 1. 检查健康状态
curl http://127.0.0.1:6000/healthz

# 2. 测试聊天
curl -X POST http://127.0.0.1:6000/v1/chat/completions \
  -H "Authorization: Bearer sk-cliproxyapi-test-key-001" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-5.5",
    "messages": [{"role": "user", "content": "Say hello"}],
    "max_tokens": 10
  }'
```

如果返回正常响应（包含 `choices` 和 `message`），说明转换成功！

---

## 🎯 总结

### 最简单的完整流程：

1. **认证**
```bash
./cli-proxy-api -codex-device-login
# 在浏览器中输入设备码完成授权
```

2. **启动服务**
```bash
nohup ./cli-proxy-api > cliproxyapi.log 2>&1 &
```

3. **测试**
```bash
curl -X POST http://127.0.0.1:6000/v1/chat/completions \
  -H "Authorization: Bearer sk-cliproxyapi-test-key-001" \
  -H "Content-Type: application/json" \
  -d '{"model": "gpt-5.5", "messages": [{"role": "user", "content": "Hello"}]}'
```

4. **使用**
   
   将你的应用或工具指向：
   - **Base URL**: `http://127.0.0.1:6000/v1`
   - **API Key**: `sk-cliproxyapi-test-key-001`

**就这么简单！你的 ChatGPT Plus 现在可以作为 API 使用了！** 🎉

---

## 📚 更多文档

- [README.md](./README.md) - 项目详细说明（英文）
- [README_CN.md](./README_CN.md) - 项目详细说明（中文）
- [STARTUP_GUIDE.md](./STARTUP_GUIDE.md) - 原始启动指南
- [GitHub 仓库](https://github.com/router-for-me/CLIProxyAPI) - 源代码和更新

---

**版本**: CLIProxyAPI 7.3.10  
**更新时间**: 2026-09-29  
**文档作者**: Claude Code
