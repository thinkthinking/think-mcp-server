"""Tool registration and handling."""
from typing import List
import mcp.types as types
from think_llm_client.utils.logger import logging
from . import article_analysis, content_analyzer, video_audio_extractor, speech_to_text

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
        types.Tool(
            name="extract_audio_from_video",
            description="从视频文件中提取音频并保存到指定位置",
            inputSchema={
                "type": "object",
                "properties": {
                    "video_url": {
                        "type": "string",
                        "description": "视频文件的URL或本地路径"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "音频输出路径，默认为 ~/.think-mcp-server/results"
                    },
                    "output_format": {
                        "type": "string",
                        "description": "输出音频格式，默认为mp3"
                    },
                    "output_filename": {
                        "type": "string",
                        "description": "输出文件名，默认从视频URL中提取"
                    }
                },
                "required": ["video_url"],
            },
        ),
        types.Tool(
            name="speech_to_text",
            description="将语音转换为文字并保存为Markdown文件",
            inputSchema={
                "type": "object",
                "properties": {
                    "audio_file": {
                        "type": "string",
                        "description": "音频文件的路径"
                    },
                    "provider": {
                        "type": "string",
                        "description": "语音识别供应商，支持 xunfei（科大讯飞）、baidu（百度）、bytedance（字节跳动），默认为baidu"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "输出路径，默认为 ~/.think-mcp-server/results"
                    },
                    "output_filename": {
                        "type": "string",
                        "description": "输出文件名，默认从音频文件名中提取"
                    }
                },
                "required": ["audio_file"],
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
    elif name == "extract_audio_from_video":
        return await video_audio_extractor.extract_audio_from_video(arguments)
    elif name == "speech_to_text":
        return await speech_to_text.speech_to_text(arguments)
    else:
        logger.error("Unknown tool: %s", name)
        raise ValueError(f"Unknown tool: {name}")
