"""Video audio extraction tool."""
import os
import subprocess
from pathlib import Path
import mcp.types as types
from think_llm_client.utils.logger import logging

# 获取模块的日志记录器
logger = logging.getLogger("think-mcp-server")


async def extract_audio_from_video(arguments: dict | None) -> list[types.TextContent]:
    """Extract audio from video file and save to specified location."""
    if not arguments or "video_url" not in arguments:
        logger.error("Missing video_url argument")
        raise ValueError("Missing video_url argument")

    video_url = arguments["video_url"]
    if not video_url:
        error_msg = "视频URL不能为空"
        logger.error(error_msg)
        return [types.TextContent(type="text", text=error_msg)]
        
    # 展开视频路径中的 ~ 符号（如果是本地文件）
    if not video_url.startswith(('http://', 'https://')):
        video_url = os.path.expanduser(video_url)
        # 检查视频文件是否存在
        if not os.path.exists(video_url):
            error_msg = f"视频文件不存在: {video_url}"
            logger.error(error_msg)
            return [types.TextContent(type="text", text=error_msg)]
    
    # 获取输出路径，如果未提供则使用默认路径
    output_path = arguments.get("output_path") or "~/.think-mcp-server/results"
    # 获取输出格式，如果未提供则默认为mp3
    output_format = arguments.get("output_format") or "mp3"
    # 获取输出文件名，如果未提供则从视频URL中提取
    output_filename = arguments.get("output_filename")

    # 展开路径中的 ~ 符号
    output_path = os.path.expanduser(output_path)
    logger.info("Using output path: %s", output_path)

    # 确保输出目录存在
    os.makedirs(output_path, exist_ok=True)
    logger.debug("Output directory created/verified: %s", output_path)

    # 如果未提供输出文件名，从视频URL中提取
    if not output_filename:
        # 从URL中提取文件名
        video_name = os.path.basename(video_url).split('?')[0]  # 移除URL参数
        # 移除扩展名
        video_name = os.path.splitext(video_name)[0]
        output_filename = f"{video_name}.{output_format}"
    elif not output_filename.endswith(f".{output_format}"):
        # 确保文件名有正确的扩展名
        output_filename = f"{output_filename}.{output_format}"

    output_file = os.path.join(output_path, output_filename)
    logger.info("Output file will be: %s", output_file)

    try:
        # 使用ffmpeg提取音频
        logger.debug("Starting audio extraction with ffmpeg")

        # 检查ffmpeg是否安装
        try:
            subprocess.run(["ffmpeg", "-version"],
                           check=True, capture_output=True)
            logger.debug("ffmpeg is installed")
        except (subprocess.SubprocessError, FileNotFoundError):
            error_msg = "ffmpeg is not installed. Please install ffmpeg to use this tool."
            logger.error(error_msg)
            return [types.TextContent(type="text", text=error_msg)]

        # 构建ffmpeg命令
        cmd = [
            "ffmpeg",
            "-i", video_url,  # 输入文件
            "-q:a", "0",      # 最高音频质量
            "-map", "a",      # 只提取音频流
            "-y",             # 覆盖输出文件（如果存在）
            output_file       # 输出文件
        ]

        logger.debug("Running command: %s", " ".join(cmd))

        # 执行命令
        process = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )

        logger.debug("ffmpeg stdout: %s", process.stdout)
        if process.stderr:
            logger.debug("ffmpeg stderr: %s", process.stderr)

        # 检查输出文件是否存在
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            logger.info(
                "Audio extraction completed successfully. File size: %d bytes", file_size)
            return [types.TextContent(
                type="text",
                text=f"音频提取成功!\n文件路径: {output_file}\n文件大小: {file_size} 字节"
            )]
        else:
            error_msg = f"Audio extraction failed. Output file not found: {output_file}"
            logger.error(error_msg)
            return [types.TextContent(type="text", text=error_msg)]

    except subprocess.CalledProcessError as e:
        error_msg = f"ffmpeg error: {e.stderr}"
        logger.error(error_msg)
        return [types.TextContent(type="text", text=error_msg)]
    except Exception as e:
        error_msg = f"Error extracting audio: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return [types.TextContent(type="text", text=error_msg)]
