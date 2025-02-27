"""Content analysis tool."""
from pathlib import Path
import yaml
import re
import os
import mcp.types as types
from think_llm_client import LLMClient
from think_llm_client.utils.logger import logging

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
    front_matter = {
        "name": path.stem,
        "description": description
    }
    return f"---\n{yaml.dump(front_matter, allow_unicode=True)}---\n"


async def analyze_content(arguments: dict | None) -> list[types.TextContent]:
    """Analyze content of a file or directory and generate front matter description."""
    if not arguments or "file_path" not in arguments:
        logger.error("Missing file_path argument")
        raise ValueError("Missing file_path argument")

    file_path = arguments["file_path"]
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
                        # Recursively call analyze_content for each file
                        file_result = await analyze_content({"file_path": str(file)})
                        results.extend(file_result)
                    except Exception as e:
                        logger.error("Error processing file %s: %s", file, str(e))
                        results.append(types.TextContent(type="text", text=f"Error processing {file.name}: {str(e)}"))
            logger.info("Processed %d files in directory", file_count)
            return results
        
        elif path.is_file():
            logger.debug("Processing single file: %s", file_path)
            description = await analyze_file_content(file_path)
            logger.debug("Got description result: %s", description)
            
            logger.debug("Generating front matter...")
            front_matter = generate_front_matter(file_path, description["text"])
            logger.debug("Front matter generated successfully")
            
            # Update the file with front matter
            content = path.read_text(encoding='utf-8')
            logger.debug("Original file content length: %d chars", len(content))
            
            # Remove existing front matter if present
            if content.startswith('---'):
                logger.debug("Removing existing front matter")
                content = re.sub(r'^---\s*\n.*?\n---\s*\n',
                                '', content, flags=re.DOTALL)
            # Add new front matter
            new_content = front_matter + content
            logger.debug("New content length with front matter: %d chars", len(new_content))
            path.write_text(new_content, encoding='utf-8')
            logger.info("File updated successfully with new front matter")
            
            return [types.TextContent(type="text", text=f"File: {file_path} {front_matter}")]
        
        else:
            error_msg = f"Path {file_path} does not exist"
            logger.error(error_msg)
            return [types.TextContent(type="text", text=f"Error: {error_msg}")]
            
    except Exception as e:
        logger.error("Error in analyze_content: %s", str(e), exc_info=True)
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]
