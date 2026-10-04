# CPA-Manager-Plus 本地使用说明（WSL）

本项目已安装 CPA-Manager-Plus 原生版，不使用 Docker。CLIProxyAPI 提供模型接口，CPA-Manager-Plus 采集请求用量、保存历史记录并提供统计网页。

## 使用前：本地安装与敏感信息配置

本文描述当前 WSL 环境。仓库只包含启动脚本和说明，不包含本机配置、面板二进制、密钥、OAuth 凭证或数据库。新机器克隆仓库后，需要先完成以下配置，不能直接运行面板启动脚本。

### 需要自行配置的敏感信息

| 配置 | 用途 | 配置位置 |
| --- | --- | --- |
| 模型调用 API Key | 客户端调用模型接口 | `config.yaml` 的 `access.api-keys` |
| CPA 管理密钥 | 面板访问代理管理接口 | `config.yaml` 的 `management.secret-key` 与 `runtime/management-key`，两处使用同一明文密钥 |
| 面板管理员密钥 | 登录 CPA-Manager-Plus | `runtime/admin-key`，使用独立密钥 |
| OAuth 凭证 | 代理访问模型提供商 | 通过项目登录命令生成，保存在 `auths/` |
| 数据加密密钥 | 加密面板保存的敏感数据 | 首次启动自动生成 `runtime/data.key`，务必随数据库备份 |

上表的 `runtime/` 指 `.tools/cpa-manager-plus/runtime/`。请为三类 API/管理/登录密钥分别生成随机值，不要使用文档示例文字作为实际密钥。可以在本地运行 `openssl rand -hex 32` 生成随机密钥，不要将输出提交到仓库。

代理首次启动可能将 `management.secret-key` 转为哈希。面板连接仍需原始明文密钥，不要把该哈希复制到 `management-key`。

### 新机器的准备步骤

1. 从 [CPA-Manager-Plus 官方 Releases](https://github.com/seakee/CPA-Manager-Plus/releases) 下载匹配架构的 Linux 原生包，按发布的 SHA256 校验文件检查，然后解压到 `.tools/cpa-manager-plus/`，确保其中存在 `cpa-manager-plus` 可执行文件。
2. 根据 `config.example.yaml` 创建本地 `config.yaml`，配置模型调用密钥和 OAuth 凭证，保留 `server.host: "127.0.0.1"`、`server.port: 8317`。
3. 设置以下配置；如已有同名区块，合并字段，不要重复添加：

   ```yaml
   management:
     allow-remote: false
     secret-key: "替换为随机生成的CPA管理密钥"
     disable-control-panel: true

   observability:
     usage:
       usage-statistics-enabled: true
       redis-usage-queue-retention-seconds: 3600
   ```

4. 创建 `.tools/cpa-manager-plus/runtime/`，将原始 CPA 管理密钥写入 `management-key`，将独立的面板登录密钥写入 `admin-key`。每个文件只保存对应密钥，不添加引号。
5. 在该目录创建 `config.json`，将下方路径占位符替换为本机项目的绝对路径：

   ```json
   {
     "httpAddr": "127.0.0.1:18317",
     "dataDir": "/你的项目绝对路径/.tools/cpa-manager-plus/runtime",
     "cpaUpstreamUrl": "http://127.0.0.1:8317",
     "managementKeyFile": "/你的项目绝对路径/.tools/cpa-manager-plus/runtime/management-key",
     "adminKeyFile": "/你的项目绝对路径/.tools/cpa-manager-plus/runtime/admin-key",
     "collectorMode": "http"
   }
   ```

6. 在支持 Linux 权限的文件系统上，将密钥文件权限设为 `600`、运行目录设为 `700`。WSL 的 `/mnt/e` 权限效果取决于挂载设置，也需要限制对应 Windows 目录的访问权限。
7. 准备代理可执行文件 `bin/cli-proxy-api`，赋予两个服务程序和启动脚本执行权限，再按下文启动。模型列表启动脚本还需要 Python 3 和 PyYAML，可先执行 `python3 -c "import yaml"` 检查；缺少依赖时，在 WSL 中安装 `python3-yaml`（例如 `sudo apt install python3-yaml`）。

本机代理配置中的 `requests.proxy-url` 如指向 `http://127.0.0.1:7890`，需要确认该代理可用；其他机器应根据自己的网络环境配置。密钥、代理地址和项目路径均为本地配置，不随本次提交上传。

## 1. 启动服务

在 WSL 中进入项目目录：

```bash
cd /mnt/e/Project/LMK/CLIProxyAPI
```

在第一个终端启动模型代理：

如果首次使用 Codex，或需要添加、重新授权 Codex 账号，先执行设备登录命令：

```bash
./bin/cli-proxy-api -config ./config.yaml -codex-device-login
```

按照终端提示打开授权网页并输入设备码，完成账号授权。此命令用于登录，不是持续运行代理服务；授权完成后，再执行下面的启动命令：

```bash
./start-with-models.sh --config ./config.yaml --local-model
```

代理地址为 `http://127.0.0.1:8317`。看到 `API server started successfully` 表示启动成功。

### 每次启动更新模型列表

`start-with-models.sh` 会启动 `bin/cli-proxy-api`，读取 `config.yaml` 的 `server` 地址和 `access.api-keys` 中的第一个调用密钥，查询 `/v1/models`，将结果保存到项目目录的 `available-models.json`。列表包含 `base_url`、`updated_at`、`status`、`model_ids` 和完整模型数据，不包含调用密钥。文件会在每次启动时覆盖更新，并已加入 Git 忽略规则。

查看当前模型 ID：

```bash
python3 -c "import json; print('\n'.join(json.load(open('available-models.json'))['model_ids']))"
```

查看导出状态、接口地址和更新时间：

```bash
python3 -c "import json; d=json.load(open('available-models.json')); print(d['status'], d['base_url'], d['updated_at'])"
```

脚本最多等待约 60 秒获取模型目录，并在非空列表稳定约 3 秒后结束采集；代理继续前台运行。`starting` 表示正在获取，`ready` 表示已获得接口返回（可能为空），`unavailable` 表示未取得有效结果。获取失败时不会沿用上次的旧模型列表，查看代理日志检查登录状态和配置。按 `Ctrl+C` 会停止代理。

这里的列表表示当前密钥通过代理 `/v1/models` 可见的模型，未逐个发起模型调用；账号权限、额度和上游状态仍可能影响实际请求。`--local-model` 使用程序内置模型目录，因此列表还受当前二进制版本影响。新增账号或修改配置后，可在下次重启时更新列表；脚本不持续监控运行期间的变化。

直接使用 `./bin/cli-proxy-api --config ./config.yaml --local-model` 不会自动导出列表。设备登录仍使用上面的原始登录命令，完成后再运行 `start-with-models.sh`。

另开一个 WSL 终端，进入同一项目目录，启动统计面板：

```bash
./start-cpa-manager.sh
```

看到 `listening on 127.0.0.1:18317` 表示面板启动成功。两个服务都需要持续运行；前台启动时，关闭终端或按 `Ctrl+C` 会停止对应服务。

如果服务已经运行，不要再次启动。

## 2. 登录网页

在 Windows 或 WSL 的浏览器中打开：

**http://127.0.0.1:18317/management.html**

在项目目录执行以下命令，查看面板登录密钥：

```bash
cat .tools/cpa-manager-plus/runtime/admin-key
```

将输出的密钥填入面板的管理员密钥登录框。不要把密钥发给其他人或提交到 Git。

当前已配置面板连接到本地代理，通常无需再次设置。如果页面要求填写连接信息，使用：

| 字段                          | 内容                      |
| ----------------------------- | ------------------------- |
| CPA 地址 / 上游地址           | `http://127.0.0.1:8317` |
| CPA Management Key / 管理密钥 | 下方命令输出的密钥        |

```bash
cat .tools/cpa-manager-plus/runtime/management-key
```

两种密钥用途不同：`admin-key` 用于登录统计面板，`management-key` 用于面板连接 CLIProxyAPI。调用模型使用的是 `config.yaml` 中 `access.api-keys` 配置的 API Key。

## 3. 查看 token 消耗

1. 保持代理和统计面板同时运行。
2. 继续让你的模型客户端请求原来的 `8317` 服务。客户端地址和调用 API Key 不需要因为安装面板而改变。
3. 完成一次模型调用后，打开面板的“请求监控”，查看新请求的模型、状态、时间及 token 用量。
4. 打开“用量分析”，选择时间范围，按模型、账号等维度查看汇总。
5. 查看成本统计时，先检查模型价格配置；费用是按照价格计算的估算值，不等于提供商账单。

不同面板版本的菜单名称可能略有不同。部分 token 字段取决于上游返回的数据，例如输入、输出、推理和缓存 token，并非所有模型都会提供全部字段。

统计从开启采集后开始，之前未保存的调用记录无法自动补回。统计面板停止期间，代理队列最多保留当前配置的 3600 秒；超过保留时间的数据可能丢失，因此需要完整历史时应保持面板运行。

## 4. 常见问题

### 提示数据库锁已被持有

```text
manager database process lock is already held
```

表示已有面板进程使用同一数据库，本次启动没有成功。先打开网页检查已有面板是否正常工作。不要删除锁文件，也不要同时运行两个面板进程。

查看监听进程：

```bash
ss -ltnp 'sport = :8317 or sport = :18317'
```

需要重启时，优先在原终端按 `Ctrl+C`；如果进程在后台运行，先确认上面显示的 PID 和进程名称，再停止指定进程：

```bash
kill -TERM <确认后的PID>
```

之后重新运行对应启动命令。

### 网页打不开

检查 `18317` 是否有监听进程，确认面板没有退出。先在 WSL 中验证网页：

```bash
curl --noproxy '*' -I http://127.0.0.1:18317/management.html
```

如果 WSL 能访问而 Windows 浏览器不能访问，检查 Windows 代理是否绕过 `localhost` 和 `127.0.0.1`，以及 WSL 的 localhost 转发设置。

### 没有用量记录

- 确认客户端实际请求的是这个项目的 `8317` 服务。
- 确认代理和面板均在运行，且查询时间范围包含刚刚的调用。
- 检查 `config.yaml` 中 `observability.usage.usage-statistics-enabled` 为 `true`。
- 确认面板的 CPA 地址和管理密钥正确；管理密钥修改后需要同步面板保存的连接信息和本地密钥文件。
- 等新请求完成后刷新页面。没有历史记录或尚未发起调用时，显示为空是正常的。

## 5. 文件位置与备份

| 文件                                               | 用途                                         |
| -------------------------------------------------- | -------------------------------------------- |
| `config.yaml`                                    | CLIProxyAPI 本地配置，包括管理密钥和用量开关 |
| `start-cpa-manager.sh`                           | 面板启动脚本                                 |
| `start-with-models.sh`                           | 代理启动及模型列表导出入口                   |
| `scripts/start_with_models.py`                   | 模型列表采集和代理进程管理                   |
| `available-models.json`                          | 每次启动更新的模型列表，不包含密钥           |
| `.tools/cpa-manager-plus/cpa-manager-plus`       | 原生面板程序                                 |
| `.tools/cpa-manager-plus/runtime/config.json`    | 面板本地配置，当前包含本机绝对路径           |
| `.tools/cpa-manager-plus/runtime/admin-key`      | 面板登录密钥                                 |
| `.tools/cpa-manager-plus/runtime/management-key` | 代理管理密钥                                 |
| `.tools/cpa-manager-plus/runtime/usage.sqlite`   | 请求历史和统计数据库                         |
| `.tools/cpa-manager-plus/runtime/data.key`       | 数据加密密钥，恢复数据时需要保留             |

`config.yaml` 和 `.tools/` 已被 Git 忽略。不要上传密钥或统计数据库。

备份时先停止统计面板，再备份整个 `runtime` 目录；不要只复制正在写入的 `usage.sqlite`，也不要遗漏 `data.key`。移动项目目录后，需要更新面板 `config.json` 中的绝对路径。
