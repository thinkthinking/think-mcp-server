"""Tool registration and handling."""
from typing import List
import mcp.types as types
from think_llm_client.utils.logger import logging
from . import article_analysis, content_analyzer

# 获取模块的日志记录器
logger = logging.getLogger("think-mcp-server")

async def list_tools() -> List[types.Tool]:
    """List all available tools."""
    logger.debug("Listing available tools")
    return [
        types.Tool(
            name="article_token_content_analysis",
            description="Analyze articles' token count and content in specified date or date range",
            inputSchema={
                "type": "object",
                "properties": {
                    "date_input": {
                        "type": "string",
                        "description": "Single date (YYYY-MM-DD) or date range (YYYY-MM-DD~YYYY-MM-DD)",
                    }
                },
                "required": ["date_input"],
            },
        ),
        types.Tool(
            name="analyze_content",
            description="Analyze content of a file or directory and generate front matter description",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to a file or directory"
                    },
                    "update_after": {
                        "type": "string",
                        "description": "只更新指定日期之后的内容，格式为 'YYYY-MM-DD'，默认为 '2025-01-01'"
                    }
                },
                "required": ["file_path"],
            },
        ),
    ]


async def call_tool(
    name: str,
    arguments: dict | None,
    session
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool execution requests."""
    logger.debug("Calling tool: %s with arguments: %s", name, arguments)
    if name == "article_token_content_analysis":
        return await article_analysis.analyze_token_content(arguments)
    elif name == "analyze_content":
        return await content_analyzer.analyze_content(arguments)
    else:
        logger.error("Unknown tool: %s", name)
        raise ValueError(f"Unknown tool: {name}")
