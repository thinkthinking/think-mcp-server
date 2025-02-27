# -*- coding: utf-8 -*-
"""MCP Server implementation."""
import os
from pathlib import Path
from dotenv import load_dotenv
from importlib.metadata import version, PackageNotFoundError
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
from pydantic import AnyUrl
from think_llm_client.utils.logger import logging
from . import tools, prompts, resources
from .init import ensure_user_config_files

# 获取日志记录器
logger = logging.getLogger("think-mcp-server")

# 确保用户配置目录和文件存在，并获取 .env 文件路径
env_path = ensure_user_config_files()

# 加载环境变量
logger.info("Loading environment variables from %s", env_path)
load_dotenv(env_path)

server = Server("think-mcp-server")

# Load prompts when server starts
prompts.load_all_prompts()


@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """List available resources from prompt directory."""
    logger.debug("Listing resources")
    return resources.list_resources()


@server.read_resource()
async def handle_read_resource(uri: AnyUrl) -> str:
    """Read a specific resource's content by its URI."""
    logger.debug("Reading resource: %s", uri)
    return resources.read_resource(uri)


@server.list_prompts()
async def handle_list_prompts() -> list[types.Prompt]:
    """List available prompts."""
    logger.debug("Listing prompts")
    return list(prompts.loaded_prompts.values())


@server.get_prompt()
async def handle_get_prompt(
    name: str, arguments: dict[str, str] | None
) -> types.GetPromptResult:
    """Get a prompt by name."""
    logger.debug("Getting prompt: %s with arguments: %s", name, arguments)
    return prompts.get_prompt_result(name, arguments)


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools."""
    logger.debug("Listing tools")
    return await tools.list_tools()


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool execution requests."""
    logger.debug("Calling tool: %s with arguments: %s", name, arguments)
    return await tools.call_tool(name, arguments, server.request_context.session)


async def main():
    """Run the server."""
    logger.info("Starting server")
    try:
        server_version = version("think-mcp-server")
    except PackageNotFoundError:
        server_version = "0.2.0"
    logger.info("Server version: %s", server_version)
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="think-mcp-server",
                server_version=server_version,
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
