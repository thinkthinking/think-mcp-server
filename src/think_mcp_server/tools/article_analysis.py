"""Article analysis tool."""
import os
from datetime import datetime
import json
import tiktoken
import mcp.types as types
from think_llm_client.utils.logger import logging

# 获取模块的日志记录器
logger = logging.getLogger("think-mcp-server")


async def analyze_token_content(arguments: dict | None) -> list[types.TextContent]:
    """Analyze articles' token count and content."""
    if not arguments or "date_input" not in arguments:
        logger.error("Missing date_input argument")
        raise ValueError("Missing date_input argument")

    date_input = arguments["date_input"]
    base_path = os.getenv("article_base_path")
    max_tokens_limit = int(os.getenv("max_tokens_limit", "89600"))

    if not base_path:
        logger.error("article_base_path not set in environment variables")
        raise ValueError("article_base_path not set in environment variables")

    # Expand ~ to user's home directory
    base_path = os.path.expanduser(base_path)
    logger.info("Using base path: %s", base_path)

    # Initialize tokenizer
    encoder = tiktoken.encoding_for_model("gpt-4")
    result = {"articles": [], "total_tokens": 0}

    # Parse date input
    if "~" in date_input:
        start_date_str, end_date_str = date_input.split("~")
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        date_list = []
        current_date = start_date
        while current_date <= end_date:
            date_list.append(current_date.strftime("%Y-%m-%d"))
            current_date = current_date.replace(day=current_date.day + 1)
    else:
        date_list = [date_input]

    logger.info("Processing dates: %s", date_list)

    # Process each date and collect articles
    articles = []
    for date_str in date_list:
        folder_path = os.path.join(base_path, date_str)
        if os.path.exists(folder_path):
            logger.debug("Processing folder: %s", folder_path)
            for filename in os.listdir(folder_path):
                if filename.endswith((".md", ".markdown", ".txt")):
                    file_path = os.path.join(folder_path, filename)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            token_count = len(encoder.encode(content))
                            article_title = os.path.splitext(filename)[0]
                            articles.append({
                                "title": article_title,
                                "date": date_str,
                                "token_count": token_count,
                                "file_path": str(file_path),
                                "content": content
                            })
                            result["total_tokens"] += token_count
                            logger.debug("Processed %s: %d tokens", filename, token_count)
                    except Exception as e:
                        logger.error("Error processing %s: %s", file_path, str(e))
                        articles.append({
                            "title": os.path.splitext(filename)[0],
                            "date": date_str,
                            "error": str(e),
                            "file_path": str(file_path),
                            "content": ""
                        })

    # Sort articles by token count in descending order
    articles.sort(key=lambda x: x.get("token_count", 0), reverse=True)

    # Process content based on max_tokens_limit
    current_total = 0
    for article in articles:
        if "error" in article:  # Skip articles with errors
            continue

        token_count = article["token_count"]
        if current_total + token_count <= max_tokens_limit:
            current_total += token_count
        else:
            # Clear content for articles that would exceed the limit
            article["content"] = ""
            logger.debug("Skipped content for %s due to token limit", article["title"])

    result["articles"] = articles
    logger.info("Total tokens processed: %d", result["total_tokens"])

    return [
        types.TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False, indent=2),
        )
    ]
