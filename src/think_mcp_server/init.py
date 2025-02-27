# -*- coding: utf-8 -*-
"""初始化模块，负责创建必要的目录和文件。"""
import os
import platform
import shutil
from pathlib import Path
from think_llm_client.utils.logger import logging
from .templates import ENV_TEMPLATE_UNIX, ENV_TEMPLATE_WINDOWS, PROMPTS_TEMPLATE, RESOURCES_TEMPLATE, CONTENT_ANALYZER_PROMPT_TEMPLATE

# 获取日志记录器
logger = logging.getLogger("think-mcp-server")

def expand_user_path(path_str: str) -> str:
    """扩展用户路径中的 ~ 符号，并根据操作系统调整路径格式。"""
    if not path_str or '~' not in path_str:
        return path_str
        
    # 获取用户主目录
    home_dir = str(Path.home())
    
    # 根据操作系统调整路径格式
    system = platform.system()
    if system == 'Windows':
        # Windows 系统中替换 ~ 为实际的用户主目录路径
        if path_str.startswith('~/'):
            return path_str.replace('~/', home_dir.replace('\\', '/') + '/')
        elif path_str.startswith('~'):
            return path_str.replace('~', home_dir.replace('\\', '/'))
    else:
        # Unix-like 系统直接使用 Path 对象的 expanduser 方法
        return str(Path(path_str).expanduser())
    
    return path_str

def create_file_if_not_exists(file_path: Path, content: str):
    """如果文件不存在，则创建文件并写入内容。"""
    if file_path.exists():
        logger.info("文件已存在: %s", file_path)
        return
        
    try:
        # 确保目标目录存在
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入文件内容
        file_path.write_text(content, encoding='utf-8')
        logger.info("创建文件: %s", file_path)
    except Exception as e:
        logger.error("创建文件 %s 失败: %s", file_path, str(e))

def ensure_user_config_files():
    """确保用户配置文件和目录存在，如果不存在则创建。"""
    # 获取用户主目录
    home_dir = Path.home()
    
    # 创建配置目录结构
    config_dir = home_dir / '.think-mcp-server' / 'config'
    prompts_dir = home_dir / '.think-mcp-server' / 'prompts'
    resources_dir = home_dir / '.think-mcp-server' / 'resources'
    
    # 创建目录
    for directory in [config_dir, prompts_dir, resources_dir]:
        directory.mkdir(parents=True, exist_ok=True)
        logger.info("确保目录存在: %s", directory)
    
    # 目标文件路径
    env_target_path = config_dir / '.env'
    prompts_target_path = prompts_dir / 'prompts-template.md'
    resources_target_path = resources_dir / 'resources-template.md'
    content_analyzer_prompt_path = resources_dir / 'tool_content_analyzer_prompt.md'
    
    # 根据操作系统选择适合的 .env 模板
    if not env_target_path.exists():
        system = platform.system()
        if system == 'Windows':
            # Windows 系统使用绝对路径
            home_str = str(home_dir).replace('\\', '/')
            env_content = ENV_TEMPLATE_WINDOWS.format(home_dir=home_str)
        else:
            # Unix-like 系统 (macOS/Linux) 使用 ~ 路径
            env_content = ENV_TEMPLATE_UNIX
            
        create_file_if_not_exists(env_target_path, env_content)
    
    # 创建其他文件（如果不存在）
    create_file_if_not_exists(prompts_target_path, PROMPTS_TEMPLATE)
    create_file_if_not_exists(resources_target_path, RESOURCES_TEMPLATE)
    create_file_if_not_exists(content_analyzer_prompt_path, CONTENT_ANALYZER_PROMPT_TEMPLATE)
    
    return env_target_path
