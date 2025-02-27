from . import server
import asyncio
from think_llm_client.utils.logger import setup_logger

# 初始化项目特定的日志配置
setup_logger("think-mcp-server")

def main():
    """Main entry point for the package."""
    asyncio.run(server.main())

# Optionally expose other important items at package level
__all__ = ['main', 'server']