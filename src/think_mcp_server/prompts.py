"""Prompt management module."""
from pathlib import Path
import os
from typing import Dict, Any, Optional
import yaml
import re
from datetime import datetime
import mcp.types as types
from think_llm_client.utils.logger import logging

# 获取模块的日志记录器
logger = logging.getLogger("think-mcp-server")

# Global variable to store loaded prompts
loaded_prompts: Dict[str, types.Prompt] = {}


def parse_front_matter(content: str) -> tuple[Dict[str, Any], str]:
    """Parse front matter and content from a markdown file."""
    front_matter_pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)'
    match = re.match(front_matter_pattern, content, re.DOTALL)
    if not match:
        raise ValueError("No valid front matter found")

    front_matter_str, content = match.groups()
    front_matter = yaml.safe_load(front_matter_str)
    return front_matter, content.strip()


def load_prompt_from_file(file_path: Path) -> Optional[types.Prompt]:
    """Load a prompt from a file with front matter."""
    try:
        content = file_path.read_text(encoding='utf-8')
        front_matter, _ = parse_front_matter(content)

        # Convert front matter arguments to PromptArgument objects
        arguments = []
        if 'arguments' in front_matter:
            for arg in front_matter['arguments']:
                arguments.append(
                    types.PromptArgument(
                        name=arg['name'],
                        description=arg['description'],
                        required=arg.get('required', True)
                    )
                )

        return types.Prompt(
            name=front_matter['name'],
            description=front_matter['description'],
            arguments=arguments
        )
    except Exception as e:
        logger.error("加载提示词文件 %s 失败: %s", file_path, str(e))
        return None


def load_all_prompts():
    """Load all prompts from the configured directories."""
    global loaded_prompts
    loaded_prompts.clear()

    # Get prompt directories from environment variable
    prompt_paths = os.getenv('prompts_path')
    if not prompt_paths:
        logger.warning("prompts_path 未在 .env 文件中设置")
        return
    
    # 支持多个路径，用逗号分隔
    paths = [p.strip() for p in prompt_paths.split(',')]
    
    for prompt_path in paths:
        # 确保 ~ 路径被正确展开
        prompt_dir = Path(os.path.expanduser(prompt_path))
        if not prompt_dir.exists() or not prompt_dir.is_dir():
            logger.warning("提示词目录 %s 不存在或不是一个目录", prompt_dir)
            continue

        # Load all .md files from the prompt directory
        for file_path in sorted(prompt_dir.glob("*.md")):
            if prompt := load_prompt_from_file(file_path):
                loaded_prompts[prompt.name] = prompt
                logger.info("从 %s 加载提示词: %s", prompt_dir, prompt.name)


def replace_variables(content: str, arguments: Dict[str, str]) -> str:
    """Replace variables in content with their values."""
    # 替换 {{today}} 为当前日期
    content = content.replace("{{今天}}", datetime.now().strftime("%Y-%m-%d"))
    
    # Replace other variables from arguments
    for key, value in arguments.items():
        content = content.replace(f"{{{{{key}}}}}", str(value))

    return content


def get_prompt_result(name: str, arguments: dict[str, str] | None) -> types.GetPromptResult:
    """Get a prompt result by name and arguments."""
    if name not in loaded_prompts:
        raise ValueError(f"Prompt '{name}' not found")

    prompt = loaded_prompts[name]

    # 获取 prompt 文件路径
    prompt_paths = os.getenv('prompts_path')
    if not prompt_paths:
        raise ValueError("prompts_path 未在 .env 文件中设置")
    
    # 支持多个路径，用逗号分隔
    paths = [p.strip() for p in prompt_paths.split(',')]
    
    # 在所有路径中查找提示词文件
    prompt_file = None
    for prompt_path in paths:
        # 确保 ~ 路径被正确展开
        prompt_dir = Path(os.path.expanduser(prompt_path))
        temp_file = prompt_dir / f"{name}.md"
        
        if temp_file.exists():
            prompt_file = temp_file
            break
        
        # 如果文件不存在，尝试加载同名的模板文件
        for file_path in prompt_dir.glob("*.md"):
            try:
                content = file_path.read_text(encoding='utf-8')
                front_matter, _ = parse_front_matter(content)
                if front_matter.get('name') == name:
                    prompt_file = file_path
                    break
            except Exception:
                continue
        
        if prompt_file:
            break

    if not prompt_file or not prompt_file.exists():
        raise ValueError(f"Prompt file for '{name}' not found in any of the configured directories")

    # 读取文件内容
    content = prompt_file.read_text(encoding='utf-8')
    _, prompt_content = parse_front_matter(content)

    # 如果提供了参数，替换变量
    if arguments:
        # 验证必需参数
        for arg in prompt.arguments:
            if arg.required and arg.name not in arguments:
                raise ValueError(f"Required argument '{arg.name}' not provided")

        prompt_content = replace_variables(prompt_content, arguments)

    # 返回 GetPromptResult 对象
    return types.GetPromptResult(
        description=prompt.description,
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text=prompt_content,
                ),
            )
        ],
    )
