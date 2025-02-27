# Think MCP Server

[![PyPI version](https://img.shields.io/pypi/v/think-mcp-server.svg)](https://pypi.org/project/think-mcp-server/)
[![Python Version](https://img.shields.io/pypi/pyversions/think-mcp-server.svg)](https://pypi.org/project/think-mcp-server/)
[![License](https://img.shields.io/pypi/l/think-mcp-server.svg)](https://github.com/thinkthinking/think-mcp-server/blob/main/LICENSE)

Think MCP Server 是一个基于 MCP 协议的服务器实现，提供了丰富的功能，包括提示词管理、资源管理和工具调用等。

## 特性

- **跨平台支持**：完全兼容 macOS、Windows 和 Linux
- **自动配置文件管理**：首次运行时自动创建必要的配置文件和目录
- **提示词模板系统**：管理和使用多种提示词模板
- **资源管理**：集中管理和访问各类资源文件
- **工具调用接口**：提供丰富的工具调用能力
  - 内容分析工具：分析文件内容，提取关键信息
  - 文章分析工具：分析文章结构和内容
- **环境变量管理**：通过 .env 文件管理配置
- **日志系统**：详细的日志记录，便于调试和监控

## 安装

### 使用 pip 安装

```bash
pip install think-mcp-server
```

### 使用 uvx 直接运行

```bash
uvx think-mcp-server
```

### 从源码安装

```bash
git clone https://github.com/thinkthinking/think-mcp-server.git
cd think-mcp-server
pip install -e .
```

## 使用方法

### 配置

首次运行时，Think MCP Server 会自动创建必要的配置文件和目录：

- `~/.think-mcp-server/config/.env`: 环境变量配置
- `~/.think-mcp-server/prompts/`: 提示词目录
- `~/.think-mcp-server/resources/`: 资源目录

### 环境变量

主要环境变量包括：

```
# 基础路径配置
prompts_path=~/.think-mcp-server/prompts
resources_path=~/.think-mcp-server/resources

# 文章分析工具配置
article_base_path=~/src_code/nas/knowledge/Articles
max_tokens_limit=89600

# 内容分析工具配置
content_analyzer_prompt_path=~/.think-mcp-server/resources/tool_content_analyzer_prompt.md
```

### 运行服务器

```bash
think-mcp-server
```

### 在 Windsurf 中配置

在 Windsurf 的 servers_config.json 中添加以下配置：

```json
{
    "mcpServers": {
        "think-mcp-server": {
            "command": "uvx",
            "args": [
                "think-mcp-server"
            ]
        }
    }
}
```

## 功能说明

### 提示词管理

服务器提供了以下提示词相关功能：

- 列出所有可用提示词：`handle_list_prompts`
- 获取特定提示词：`handle_get_prompt`
- 支持动态参数替换

### 资源管理

服务器提供了以下资源相关功能：

- 读取特定资源：`handle_read_resource`
- 自动管理资源文件路径

### 工具调用

服务器提供了以下工具：

- 内容分析工具：分析文件内容，提取关键信息
- 文章分析工具：分析文章结构和内容

## 开发

### 安装开发依赖

```bash
pip install -e ".[dev]"
```

### 运行测试

```bash
pytest
```

### 构建和发布

项目使用 GitHub Actions 自动发布到 PyPI。当推送新的版本标签（如 `v0.4.1`）时，将自动触发构建和发布流程。

## 许可证

MIT

## 作者

- thinkthinking (yezhenjie@outlook.de)