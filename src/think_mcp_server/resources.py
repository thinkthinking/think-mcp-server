"""Resource management module."""
from pathlib import Path
import os
from typing import List, Optional, Dict
import mcp.types as types
from pydantic import AnyUrl
import yaml
import urllib.parse
from think_llm_client.utils.logger import logging

# 获取模块的日志记录器
logger = logging.getLogger("think-mcp-server")

def parse_frontmatter(content: str) -> tuple[Optional[Dict], str]:
    """Parse frontmatter from content.
    
    Returns:
        tuple: (frontmatter dict or None, remaining content)
    """
    if not content.startswith('---\n'):
        return None, content
        
    parts = content.split('---\n', 2)
    if len(parts) < 3:
        return None, content
        
    try:
        frontmatter = yaml.safe_load(parts[1])
        return frontmatter, parts[2]
    except yaml.YAMLError:
        logger.warning("Failed to parse frontmatter in content")
        return None, content

def list_resources() -> List[types.Resource]:
    """List available resources from resources directory."""
    resources = []

    # 从环境变量获取资源目录路径
    resources_path = os.getenv('resources_path', '')
    if not resources_path:
        logger.warning("resources_path not set in .env file")
        return resources

    # 处理所有的资源目录
    for resource_dir in resources_path.split(','):
        resource_dir = resource_dir.strip()
        if not resource_dir:
            continue
            
        # 使用 Path 对象处理路径，确保 ~ 路径被正确展开
        base_dir = Path(os.path.expanduser(resource_dir))
        if not base_dir.exists():
            logger.warning(f"资源目录不存在: {resource_dir}")
            continue

        # 添加资源目录中的文件
        for file_path in sorted(base_dir.glob("*")):
            if file_path.is_file():
                absolute_path = file_path.absolute()
                try:
                    content = file_path.read_text(encoding='utf-8')
                    frontmatter, _ = parse_frontmatter(content)
                    
                    # 使用文件名作为资源名称，确保它是解码后的
                    file_name = file_path.name
                    decoded_file_name = urllib.parse.unquote(file_name)
                    
                    description = (
                        frontmatter.get('description', f"Resource file: {decoded_file_name}")
                        if frontmatter else f"Resource file: {decoded_file_name}"
                    )
                    
                    resources.append(
                        types.Resource(
                            uri=AnyUrl(f"file://{absolute_path}"),
                            name=decoded_file_name,
                            description=description,
                            mimeType="text/plain",
                        )
                    )
                except Exception as e:
                    logger.warning(f"处理文件 {file_path} 失败: {e}")

    return sorted(resources, key=lambda x: x.name)

def read_resource(uri: AnyUrl) -> str:
    """Read a specific resource's content by its URI."""
    logger.debug(f"Reading resource: {uri}")
    
    if uri.scheme == "file":
        # 对URL编码的路径进行解码
        decoded_path = urllib.parse.unquote(uri.path)
        file_path = Path(decoded_path)
        
        if file_path.exists() and file_path.is_file():
            logger.info(f"Found resource at {file_path}")
            try:
                return file_path.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                # 如果UTF-8解码失败，尝试使用系统默认编码
                logger.warning(f"UTF-8 decode failed for {file_path}, trying with default encoding")
                return file_path.read_text()
                
        logger.error(f"File not found: {decoded_path}")
        raise ValueError(f"File not found: {decoded_path}")
    
    logger.error(f"Unsupported URI scheme: {uri.scheme}")
    raise ValueError(f"Unsupported URI scheme: {uri.scheme}")
