# Configuration Guide

This guide explains how to configure DeerFlow for your environment.

## Configuration Sections

### Models

Configure the LLM models available to the agent:

```yaml
models:
  - name: gpt-4                    # Internal identifier
    display_name: GPT-4            # Human-readable name
    use: langchain_openai:ChatOpenAI  # LangChain class path
    model: gpt-4                   # Model identifier for API
    api_key: $OPENAI_API_KEY       # API key (use env var)
    max_tokens: 4096               # Max tokens per request
    temperature: 0.7               # Sampling temperature
```

**Supported Providers**:
- OpenAI (`langchain_openai:ChatOpenAI`)
- Anthropic (`langchain_anthropic:ChatAnthropic`)
- DeepSeek (`langchain_deepseek:ChatDeepSeek`)
- Any LangChain-compatible provider

**Thinking Models**:
Some models support "thinking" mode for complex reasoning:

```yaml
models:
  - name: deepseek-v3
    supports_thinking: true
    when_thinking_enabled:
      extra_body:
        thinking:
          type: enabled
```

**模型配置字段说明（Schema）**：

配置标准由 `backend/src/config/model_config.py` 中的 `ModelConfig`（Pydantic）定义：

| 字段 | 必填 | 说明 |
|------|------|------|
| `name` | 是 | 唯一标识，用于 API/前端选择模型 |
| `use` | 是 | LangChain 模型类路径，如 `langchain_openai:ChatOpenAI` |
| `model` | 是 | 传给厂商 API 的模型名 |
| `display_name` | 否 | 展示名称，默认 None |
| `description` | 否 | 描述，默认 None |
| `supports_vision` | 否 | 是否支持图像输入（view_image 等），默认 false |
| `supports_thinking` | 否 | 是否支持思考模式，默认 false |
| `when_thinking_enabled` | 否 | 开启思考时追加的请求体（如 extra_body） |

以 `$` 开头的值会从环境变量解析（如 `$OPENAI_API_KEY`）。除上述字段外，**允许任意额外字段**（`extra="allow"`），例如 `api_key`、`api_base`、`max_tokens`、`temperature` 等，会原样传给 `use` 指定的类。

**不同供应商的配置应对齐哪里？必须配置项有哪些？**

- **对齐来源**：config 里每个模型条目的 YAML 键（除 DeerFlow 保留字段外）会**原样**传给对应 LangChain 类的构造函数，因此：
  - **参数名、是否必填、可选值**以 **LangChain 官方文档** 为准（见下表链接）。
  - 若使用代理、自建或兼容 OpenAI 的第三方（如部分国产大模型），再参考该厂商的 API 文档（base_url、模型名、鉴权方式等）。
- **DeerFlow 层必须项**（所有供应商通用）：`name`、`use`、`model`。其余为可选；`api_key` 等由各 LangChain 包决定是否必填（多数可从环境变量读取）。

| 供应商 | LangChain 类路径 (`use`) | 官方文档（对齐用） | 通常必配项 | 常用可选 |
|--------|---------------------------|---------------------|------------|----------|
| **OpenAI** | `langchain_openai:ChatOpenAI` | [ChatOpenAI Reference](https://reference.langchain.com/python/integrations/langchain_openai/ChatOpenAI/) | `model`（`api_key` 可从 `OPENAI_API_KEY` 读取） | `api_key`, `base_url`, `max_tokens`, `temperature`, `timeout`, `max_retries` |
| **Anthropic** | `langchain_anthropic:ChatAnthropic` | [ChatAnthropic](https://reference.langchain.com/python/integrations/langchain_anthropic/ChatAnthropic/) | `model`（API 钥可从 `ANTHROPIC_API_KEY` 读取） | `anthropic_api_key`, `max_tokens`, `temperature`, `timeout` |
| **DeepSeek** | `langchain_deepseek:ChatDeepSeek` | [DeepSeek 集成](https://python.langchain.com/docs/integrations/chat/deepseek/) | `model`（`api_key` 可从 `DEEPSEEK_API_KEY` 读取） | `api_key`, `api_base`, `max_tokens`, `temperature`, `timeout` |
| **兼容 OpenAI 的第三方（Kimi/豆包等）** | `src.models.patched_deepseek:PatchedChatDeepSeek` 或 `langchain_deepseek:ChatDeepSeek` | 同上 + 厂商 API 文档 | `model`、`api_base`（厂商 endpoint）、`api_key`（厂商钥） | `max_tokens`, `temperature`, 思考模式见下 |

说明：

- **api_base / base_url**：走第三方或自建时必配，指向该厂商的 API 根地址（如 Kimi `https://api.moonshot.cn/v1`、豆包 `https://ark.cn-beijing.volces.com/api/v3`）。
- **思考 / reasoning 模式**：若厂商支持“思考”并需在请求里开启，需同时设 `supports_thinking: true` 和 `when_thinking_enabled`（例如 `extra_body.thinking.type: enabled`），具体字段以厂商 API 文档为准。
- **Anthropic**：若使用 `langchain_anthropic`，注意参数名可能是 `anthropic_api_key` / `anthropic_api_url`，与 OpenAI 的 `api_key` / `base_url` 不同，需按官方 Reference 填写。

**如何验证模型配置是否成功**：

1. **仅校验配置加载与实例化**（不调用 API）  
   在 `backend` 目录执行：
   ```bash
   python scripts/verify_models.py
   ```
2. **校验并真实调用一次模型**（会消耗 API 额度）：
   ```bash
   python scripts/verify_models.py --invoke
   ```
3. **通过 Gateway API 查看已配置模型**（需先启动 Gateway）：
   ```bash
   curl http://localhost:8001/api/models
   curl http://localhost:8001/api/models/gpt-4
   ```

### Tool Groups

Organize tools into logical groups:

```yaml
tool_groups:
  - name: web          # Web browsing and search
  - name: file:read    # Read-only file operations
  - name: file:write   # Write file operations
  - name: bash         # Shell command execution
```

### Tools

Configure specific tools available to the agent:

```yaml
tools:
  - name: web_search
    group: web
    use: src.community.tavily.tools:web_search_tool
    max_results: 5
    # api_key: $TAVILY_API_KEY  # Optional
```

**Built-in Tools**:
- `web_search` - Search the web (Tavily)
- `web_fetch` - Fetch web pages (Jina AI)
- `ls` - List directory contents
- `read_file` - Read file contents
- `write_file` - Write file contents
- `str_replace` - String replacement in files
- `bash` - Execute bash commands

### Sandbox

DeerFlow supports multiple sandbox execution modes. Configure your preferred mode in `config.yaml`:

**Local Execution** (runs sandbox code directly on the host machine):
```yaml
sandbox:
   use: src.sandbox.local:LocalSandboxProvider # Local execution
```

**Docker Execution** (runs sandbox code in isolated Docker containers):
```yaml
sandbox:
   use: src.community.aio_sandbox:AioSandboxProvider # Docker-based sandbox
```

**Docker Execution with Kubernetes** (runs sandbox code in Kubernetes pods via provisioner service):

This mode runs each sandbox in an isolated Kubernetes Pod on your **host machine's cluster**. Requires Docker Desktop K8s, OrbStack, or similar local K8s setup.

```yaml
sandbox:
   use: src.community.aio_sandbox:AioSandboxProvider
   provisioner_url: http://provisioner:8002
```

See [Provisioner Setup Guide](docker/provisioner/README.md) for detailed configuration, prerequisites, and troubleshooting.

Choose between local execution or Docker-based isolation:

**Option 1: Local Sandbox** (default, simpler setup):
```yaml
sandbox:
  use: src.sandbox.local:LocalSandboxProvider
```

**Option 2: Docker Sandbox** (isolated, more secure):
```yaml
sandbox:
  use: src.community.aio_sandbox:AioSandboxProvider
  port: 8080
  auto_start: true
  container_prefix: deer-flow-sandbox

  # Optional: Additional mounts
  mounts:
    - host_path: /path/on/host
      container_path: /path/in/container
      read_only: false
```

### Skills

Configure the skills directory for specialized workflows:

```yaml
skills:
  # Host path (optional, default: ../skills)
  path: /custom/path/to/skills

  # Container mount path (default: /mnt/skills)
  container_path: /mnt/skills
```

**How Skills Work**:
- Skills are stored in `deer-flow/skills/{public,custom}/`
- Each skill has a `SKILL.md` file with metadata
- Skills are automatically discovered and loaded
- Available in both local and Docker sandbox via path mapping

### Title Generation

Automatic conversation title generation:

```yaml
title:
  enabled: true
  max_words: 6
  max_chars: 60
  model_name: null  # Use first model in list
```

## Environment Variables

DeerFlow supports environment variable substitution using the `$` prefix:

```yaml
models:
  - api_key: $OPENAI_API_KEY  # Reads from environment
```

**Common Environment Variables**:
- `OPENAI_API_KEY` - OpenAI API key
- `ANTHROPIC_API_KEY` - Anthropic API key
- `DEEPSEEK_API_KEY` - DeepSeek API key
- `TAVILY_API_KEY` - Tavily search API key
- `DEER_FLOW_CONFIG_PATH` - Custom config file path

## Configuration Location

The configuration file should be placed in the **project root directory** (`deer-flow/config.yaml`), not in the backend directory.

## Configuration Priority

DeerFlow searches for configuration in this order:

1. Path specified in code via `config_path` argument
2. Path from `DEER_FLOW_CONFIG_PATH` environment variable
3. `config.yaml` in current working directory (typically `backend/` when running)
4. `config.yaml` in parent directory (project root: `deer-flow/`)

## Best Practices

1. **Place `config.yaml` in project root** - Not in `backend/` directory
2. **Never commit `config.yaml`** - It's already in `.gitignore`
3. **Use environment variables for secrets** - Don't hardcode API keys
4. **Keep `config.example.yaml` updated** - Document all new options
5. **Test configuration changes locally** - Before deploying
6. **Use Docker sandbox for production** - Better isolation and security

## Troubleshooting

### "Config file not found"
- Ensure `config.yaml` exists in the **project root** directory (`deer-flow/config.yaml`)
- The backend searches parent directory by default, so root location is preferred
- Alternatively, set `DEER_FLOW_CONFIG_PATH` environment variable to custom location

### "Invalid API key"
- Verify environment variables are set correctly
- Check that `$` prefix is used for env var references

### "Skills not loading"
- Check that `deer-flow/skills/` directory exists
- Verify skills have valid `SKILL.md` files
- Check `skills.path` configuration if using custom path

### "Docker sandbox fails to start"
- Ensure Docker is running
- Check port 8080 (or configured port) is available
- Verify Docker image is accessible

## Examples

See `config.example.yaml` for complete examples of all configuration options.
