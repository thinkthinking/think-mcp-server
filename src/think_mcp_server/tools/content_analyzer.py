"""Content analysis tool."""
from pathlib import Path
import yaml
import re
import os
import mcp.types as types
from think_llm_client import LLMClient
from think_llm_client.utils.logger import logging
from datetime import datetime

# 获取模块的日志记录器
logger = logging.getLogger("think-mcp-server")

async def analyze_file_content(file_path: str) -> dict:
    """Analyze file content using LLM and return a description."""
    try:
        client = LLMClient()
        logger.debug("LLM client created successfully")
        model_type = "llm"
        model_provider = "硅基流动"
        model_name = "Pro/deepseek-ai/DeepSeek-V3"
        client.set_model(model_type, model_provider, model_name)
        logger.debug("Model set to %s/%s/%s", model_type, model_provider, model_name)

        # Read file content
        path = Path(file_path)
        if not path.is_file():
            logger.error("Path is not a file: %s", file_path)
            raise ValueError(f"Path {file_path} is not a file")

        logger.info("Analyzing file: %s", file_path)
        prompt_path = os.getenv('content_analyzer_prompt_path')
        if prompt_path is None:
            logger.error("content_analyzer_prompt_path environment variable not set")
            raise ValueError("content_analyzer_prompt_path environment variable not set")
        logger.debug("Using prompt template from: %s", prompt_path)
        
        # 展开路径中的 ~ 符号
        prompt_path = os.path.expanduser(prompt_path)
        
        if not os.path.exists(prompt_path):
            logger.error("Prompt template file not found at: %s", prompt_path)
            raise FileNotFoundError(f"Prompt template file not found at: {prompt_path}")
            
        with open(str(prompt_path), 'r', encoding='utf-8') as f:
            prompt_template = f.read().strip()
        logger.debug("Prompt template loaded successfully")
        
        content = path.read_text(encoding='utf-8')
        logger.debug("File content loaded successfully, length: %d chars", len(content))
        
        # Call LLM to analyze content
        logger.debug("Sending request to LLM...")
        _, response = await client.chat(f"{prompt_template}：\n\n{content}", stream=False)
        logger.debug("Received response from LLM, length: %d chars", len(response))
        return {"type": "text", "text": response}
    except Exception as e:
        logger.error("Error analyzing content: %s", str(e), exc_info=True)
        return {"type": "text", "text": f"Error analyzing content: {str(e)}"}

def generate_front_matter(file_path: str, description: str) -> str:
    """Generate front matter for a file."""
    path = Path(file_path)
    current_time = datetime.now().strftime("%Y-%m-%d")
    front_matter = {
        "name": path.stem,
        "description": description,
        "edit_time": current_time
    }
    return f"---\n{yaml.dump(front_matter, allow_unicode=True)}---\n"


async def analyze_content(arguments: dict | None) -> list[types.TextContent]:
    """Analyze content of a file or directory and generate front matter description."""
    if not arguments or "file_path" not in arguments:
        logger.error("Missing file_path argument")
        raise ValueError("Missing file_path argument")

    file_path = arguments["file_path"]
    # 获取更新截止日期，如果未提供则为2025-01-01
    update_after = arguments.get("update_after", "2025-01-01")
    logger.info("Starting content analysis for: %s", file_path)
    results = []

    try:
        path = Path(file_path)
        
        if path.is_dir():
            logger.info("Processing directory: %s", file_path)
            file_count = 0
            for file in path.rglob('*'):
                if file.is_file():
                    file_count += 1
                    logger.debug("[%d] Processing file: %s", file_count, file)
                    try:
                        # 递归调用时传递update_after参数
                        file_args = {"file_path": str(file)}
                        if update_after:
                            file_args["update_after"] = update_after
                        file_result = await analyze_content(file_args)
                        results.extend(file_result)
                    except Exception as e:
                        logger.error("Error processing file %s: %s", file, str(e))
                        results.append(types.TextContent(type="text", text=f"Error processing {file.name}: {str(e)}"))
            logger.info("Processed %d files in directory", file_count)
            return results
        
        elif path.is_file():
            logger.debug("Processing single file: %s", file_path)
            
            # 检查是否需要更新
            should_update = True
            content = path.read_text(encoding='utf-8')
            
            # 如果指定了更新截止日期，检查文件的edit_time
            if update_after and content.startswith('---'):
                try:
                    # 提取现有的front matter
                    front_matter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
                    if front_matter_match:
                        existing_front_matter = yaml.safe_load(front_matter_match.group(1))
                        if "edit_time" in existing_front_matter:
                            file_edit_time = datetime.strptime(existing_front_matter["edit_time"], "%Y-%m-%d")
                            update_after_time = datetime.strptime(update_after, "%Y-%m-%d")
                            # 如果文件的编辑时间晚于指定的更新截止日期，则不需要更新
                            if file_edit_time > update_after_time:
                                logger.info("File %s was updated after %s, skipping", file_path, update_after)
                                should_update = False
                except Exception as e:
                    logger.warning("Error parsing front matter for date check: %s", str(e))
                    # 如果解析出错，继续更新文件
            
            if should_update:
                description = await analyze_file_content(file_path)
                logger.debug("Got description result: %s", description)
                
                logger.debug("Generating front matter...")
                front_matter = generate_front_matter(file_path, description["text"])
                logger.debug("Front matter generated successfully")
                
                # 更新文件的front matter
                logger.debug("Original file content length: %d chars", len(content))
                
                # 移除现有的front matter（如果存在）
                if content.startswith('---'):
                    logger.debug("Removing existing front matter")
                    content = re.sub(r'^---\s*\n.*?\n---\s*\n',
                                    '', content, flags=re.DOTALL)
                # 添加新的front matter
                new_content = front_matter + content
                logger.debug("New content length with front matter: %d chars", len(new_content))
                path.write_text(new_content, encoding='utf-8')
                logger.info("File updated successfully with new front matter")
                
                return [types.TextContent(type="text", text=f"File: {file_path} {front_matter}")]
            else:
                return [types.TextContent(type="text", text=f"File: {file_path} - No update needed (last edit was after {update_after})")]
        
        else:
            error_msg = f"Path {file_path} does not exist"
            logger.error(error_msg)
            return [types.TextContent(type="text", text=f"Error: {error_msg}")]
            
    except Exception as e:
        logger.error("Error in analyze_content: %s", str(e), exc_info=True)
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]
