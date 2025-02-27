# think-mcp MCP server

thinkthinking's mcp server

## Install

<https://modelcontextprotocol.io/quickstart/server>
<https://github.com/modelcontextprotocol/create-python-server>
<https://github.com/modelcontextprotocol/python-sdk>
<https://github.com/modelcontextprotocol/servers>

```bash
# install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

uvx create-mcp-server

# Create virtual environment and activate it
uv venv
source .venv/bin/activate

my-server/
├── README.md
├── pyproject.toml
└── src/
    └── my_server/
        ├── __init__.py
        ├── __main__.py
        └── server.py

uv --directory /Users/thinkthinking/src_code/nas/think-mcp run think-mcp
```

## Components

### Resources

The server implements a simple note storage system with:

- Custom note:// URI scheme for accessing individual notes
- Each note resources has a name, description and text/plain mimetype

### Prompts

The server provides a single prompt:

- summarize-notes: Creates summaries of all stored notes
  - Optional "style" argument to control detail level (brief/detailed)
  - Generates prompt combining all current notes with style preference

### Tools

The server implements several tools:

- add-note: Adds a new note to the server
  - Takes "name" and "content" as required string arguments
  - Updates server state and notifies clients of resources changes
  
- content-analyzer: Analyzes file content using LLM
  - Supports both single file and directory analysis
  - Generates front matter with descriptions
  - Handles various file types and formats

### 日志系统

本项目使用 `think-llm-client` 包提供的日志系统，统一管理所有日志输出：

```python
from think_llm_client.utils.logger import logging

# 获取项目日志记录器
logger = logging.getLogger("think-mcp-server")

# 使用日志
logger.info("这是一条信息日志")
logger.debug("这是一条调试日志")
logger.warning("这是一条警告日志")
logger.error("这是一条错误日志")
```

日志配置在项目初始化时通过 `setup_logger` 函数完成：

```python
from think_llm_client.utils.logger import setup_logger

# 初始化项目特定的日志配置
setup_logger("think-mcp-server")
```

日志文件位置可以通过以下方式获取：

```python
from think_llm_client.utils.logger import get_log_file_path

log_file = get_log_file_path("think-mcp-server")
```

## Development

### Package Management

本项目使用 `uv` 作为包管理器，`pyproject.toml` 作为依赖配置文件。以下是常用的依赖管理操作：

```bash
# 安装所有依赖
uv pip install -e .

# 安装开发依赖
uv pip install pytest pytest-asyncio pytest-mock

# 更新依赖
uv pip install --upgrade [package-name]
```

### Running Tests

项目使用 pytest 进行单元测试。测试文件位于 `tests/` 目录下。以下是运行测试的方法：

```bash
# 运行所有测试
python -m pytest

# 运行特定测试文件
python -m pytest tests/think_mcp/tools/test_content_analyzer.py

# 运行特定测试用例
python -m pytest tests/think_mcp/tools/test_content_analyzer.py -k "test_analyze_file_content"

# 显示详细输出
python -m pytest -v

# 显示测试覆盖率
python -m pytest --cov=think_mcp
```

测试用例包括：

1. 单文件分析测试
   - 测试文件内容分析
   - 测试前置信息生成
   - 测试错误处理

2. 目录分析测试
   - 测试多文件批量分析
   - 测试结果合并

3. 边界条件测试
   - 测试不存在的文件/目录
   - 测试无参数情况
   - 测试异常处理

### Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Write and run tests for your changes
4. Commit your changes (`git commit -m 'Add some amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

# MCP Inspector Server 调试

```bash
npx @modelcontextprotocol/inspector uv --directory /Users/thinkthinking/src_code/nas/think-mcp run think-mcp
npx @modelcontextprotocol/inspector@0.2.0 uv --directory /Users/thinkthinking/src_code/nas/think-mcp run think-mcp

npx @modelcontextprotocol/inspector@0.2.0 \
  uv \
  --directory  /Users/thinkthinking/src_code/nas/think-mcp \
  run \
  think-mcp

npx @modelcontextprotocol/inspector@0.3.0 \
  /Users/thinkthinking/src_code/nas/think-mcp/.venv/bin/uv \
  --directory  /Users/thinkthinking/src_code/nas/think-mcp \
  run \
  think-mcp

```

# Tools 调试

## content-analyzer调试

```bash

# From the project root directory:
python tests/think_mcp/tools/run_content_analyzer.py /Users/thinkthinking/src_code/nas/think-mcp/resources/prompts
# Or from the tests/think_mcp/tools directory:
python run_content_analyzer.py resources/docs