# CLIProxyAPI 配置与启动指南

## 一、配置步骤

### 1. 获取 ChatGPT Plus Access Token

在已登录 ChatGPT Plus 的浏览器中：

1. 打开 ChatGPT 网站 (https://chatgpt.com)
2. 按 `F12` 打开开发者工具
3. 切换到 `Console`（控制台）标签页
4. 在控制台中粘贴并执行以下代码：

```javascript
fetch('https://chatgpt.com/api/auth/session')
  .then(r=>r.json())
  .then(d=>console.log('Access Token:\n'+d.accessToken))
```

5. 复制输出的 Access Token（以 `eyJ` 开头的长字符串）

### 2. 创建认证文件

将获取到的 Access Token 保存到认证文件：

```bash
mkdir -p ~/.cli-proxy-api

cat > ~/.cli-proxy-api/codex_你的邮箱@gmail.com.json <<'EOF'
{
  "type": "codex",
  "email": "你的邮箱@gmail.com",
  "access_token": "这里粘贴你的Access Token"
}
EOF
```

**示例**（已配置的文件）：
- 位置：`~/.cli-proxy-api/codex_zishanozty@gmail.com.json`
- 格式：
```json
{
  "type": "codex",
  "email": "zishanozty@gmail.com",
  "access_token": "eyJhbGciOiJS..."
}
```

### 3. 配置 API Key（可选）

API Key 在配置文件中设置：

**配置文件位置**：`/mnt/nvme1n1/data/lmk/Github/CLIProxyAPI/config.yaml`

**API Key 配置**（第 39-40 行）：
```yaml
api-keys:
  - "sk-cliproxyapi-test-key-001"
```

可以添加多个 API Key，修改后需要重启服务。

## 二、启动服务

### 方法一：前台启动（开发调试用）

```bash
cd /mnt/nvme1n1/data/lmk/Github/CLIProxyAPI
./cli-proxy-api
```

按 `Ctrl+C` 停止服务。

### 方法二：后台启动（推荐）

```bash
cd /mnt/nvme1n1/data/lmk/Github/CLIProxyAPI
nohup ./cli-proxy-api > cliproxyapi.log 2>&1 &
```

## 三、服务管理

### 查看进程状态

```bash
ps aux | grep cli-proxy-api | grep -v grep
```

### 查看日志

```bash
# 查看启动日志
tail -f /mnt/nvme1n1/data/lmk/Github/CLIProxyAPI/cliproxyapi.log

# 或查看详细日志
tail -f /mnt/nvme1n1/data/lmk/Github/CLIProxyAPI/service.log
```

### 停止服务

```bash
pkill -f cli-proxy-api
```

### 重启服务

```bash
pkill -f cli-proxy-api
cd /mnt/nvme1n1/data/lmk/Github/CLIProxyAPI
nohup ./cli-proxy-api > cliproxyapi.log 2>&1 &
```

## 四、服务信息

### 访问地址

- **基础 URL**: `http://127.0.0.1:6000`
- **模型列表**: `http://127.0.0.1:6000/v1/models`
- **对话接口**: `http://127.0.0.1:6000/v1/chat/completions`

### API Key

- **当前 Key**: `sk-cliproxyapi-test-key-001`
- **配置位置**: `config.yaml` 第 39-40 行

### 测试服务

```bash
curl -H "Authorization: Bearer sk-cliproxyapi-test-key-001" \
  http://127.0.0.1:6000/v1/models
```

成功响应示例：
```json
{
    "data": [
        {
            "id": "gpt-5.5",
            "object": "model",
            "owned_by": "openai"
        },
        ...
    ]
}
```

## 五、集成到 cc-switch

### 添加为 Provider

CLIProxyAPI 启动后，可以在 cc-switch 中添加为 provider：

- **Provider 名称**: 自定义（如：cliproxyapi-codex）
- **API URL**: `http://127.0.0.1:6000`
- **API Key**: `sk-cliproxyapi-test-key-001`
- **类型**: OpenAI Compatible

配置完成后，可以在 Claude Code 中通过 cc-switch 切换使用 ChatGPT Codex。

## 六、常见问题

### 1. 服务无法启动

检查端口 6000 是否被占用：
```bash
lsof -i:6000
```

### 2. 认证失败

- 确认 Access Token 是否过期（有效期约 10 天）
- 重新获取 Access Token 并更新认证文件

### 3. API Key 错误

确认请求头格式正确：
```
Authorization: Bearer sk-cliproxyapi-test-key-001
```

### 4. 查看详细错误

查看日志文件获取详细错误信息：
```bash
tail -100 /mnt/nvme1n1/data/lmk/Github/CLIProxyAPI/cliproxyapi.log
```
