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
        logger.error("Error loading prompt from %s: %s", file_path, str(e))
        return None


def load_all_prompts():
    """Load all prompts from the configured directory."""
    global loaded_prompts
    loaded_prompts.clear()

    # Get prompt directory from environment variable
    prompt_path = os.getenv('PROMPTS_PATH')
    if not prompt_path:
        logger.warning("PROMPTS_PATH not set in .env file")
        return

    prompt_dir = Path(prompt_path)
    if not prompt_dir.exists() or not prompt_dir.is_dir():
        logger.warning(
            "Prompt directory %s does not exist or is not a directory", prompt_dir)
        return

    # Load all .md files from the prompt directory
    for file_path in sorted(prompt_dir.glob("*.md")):
        if prompt := load_prompt_from_file(file_path):
            loaded_prompts[prompt.name] = prompt


def replace_variables(content: str, arguments: Dict[str, str]) -> str:
    """Replace variables in content with their values."""
    # Replace {{today}} with current date
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
    prompt_path = os.getenv('PROMPTS_PATH')
    if not prompt_path:
        raise ValueError("PROMPTS_PATH not set in .env file")

    prompt_dir = Path(prompt_path)
    prompt_file = prompt_dir / f"{name}.md"

    if not prompt_file.exists():
        raise ValueError(f"Prompt file for '{name}' not found")

    # 读取文件内容并解析
    content = prompt_file.read_text(encoding='utf-8')
    _, prompt_content = parse_front_matter(content)

    # 替换变量
    processed_content = replace_variables(prompt_content, arguments or {})

    return types.GetPromptResult(
        description=prompt.description,
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text=processed_content,
                ),
            )
        ],
    )
