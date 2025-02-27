# Think MCP Server

[![PyPI version](https://img.shields.io/pypi/v/think-mcp-server.svg)](https://pypi.org/project/think-mcp-server/)
[![Python Version](https://img.shields.io/pypi/pyversions/think-mcp-server.svg)](https://pypi.org/project/think-mcp-server/)
[![License](https://img.shields.io/pypi/l/think-mcp-server.svg)](https://github.com/thinkthinking/think-mcp-server/blob/main/LICENSE)

Think MCP Server 是一个基于 MCP 协议的服务器实现，提供了丰富的功能，包括提示词管理、资源管理和工具调用等。

## 特性

- 跨平台支持 (macOS, Windows, Linux)
- 自动配置文件管理
- 提示词模板系统
- 资源管理
- 工具调用接口

## 安装

### 使用 pip 安装

```bash
pip install think-mcp-server
```

### 使用 uvx 直接运行

```bash
uvx run think-mcp-server
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
        "run",
        "think-mcp-server"
      ]
    }
  }
}
```

## 开发

### 安装开发依赖

```bash
pip install -e ".[dev]"
```

### 运行测试

```bash
pytest
```

## 许可证

MIT

## 作者

- 叶震杰 (yezhenjie@outlook.de)