"""语音转文字工具。"""
import os
import json
from datetime import datetime
from pathlib import Path
import mcp.types as types
from think_llm_client.utils.logger import logging

# 导入语音识别模块
from .baidu_speech_recognizer import BaiduSpeechRecognizer

# 获取模块的日志记录器
logger = logging.getLogger("think-mcp-server")


class BytedanceSpeechRecognizer:
    """字节跳动语音识别实现"""
    
    def __init__(self, app_id, api_key, secret_key, audio_file):
        """初始化字节跳动语音识别参数"""
        self.app_id = app_id
        self.api_key = api_key
        self.secret_key = secret_key
        self.audio_file = audio_file
    
    async def recognize(self):
        """执行语音识别"""
        # 这里是字节跳动语音识别的实现
        # 此处为示例，实际使用时需要根据字节跳动API文档进行完整实现
        logger.info("字节跳动语音识别功能尚未完全实现")
        return "字节跳动语音识别功能尚未完全实现，请使用百度语音识别。"


class XunfeiOSTRecognizer:
    """科大讯飞离线语音识别实现（占位）"""
    
    def __init__(self, app_id, api_key, api_secret):
        """初始化科大讯飞离线语音识别参数"""
        self.app_id = app_id
        self.api_key = api_key
        self.api_secret = api_secret
    
    async def recognize(self, audio_file):
        """执行语音识别（占位）"""
        logger.info("科大讯飞语音识别功能已简化为占位实现")
        return "科大讯飞语音识别功能已简化为占位实现，请使用百度语音识别。"


def get_provider_credentials(provider):
    """从环境变量中获取指定供应商的API凭证"""
    logger.info("Getting credentials for provider: %s", provider)
    
    if provider.lower() == "baidu":
        app_id = os.getenv("baidu_app_id")
        api_key = os.getenv("baidu_api_key")
        secret_key = os.getenv("baidu_secret_key")
        
        if not all([app_id, api_key, secret_key]):
            logger.warning("百度API凭证不完整，请在环境变量中设置 baidu_app_id, baidu_api_key, baidu_secret_key")
        
        return {
            "app_id": app_id,
            "api_key": api_key,
            "secret_key": secret_key
        }
    
    elif provider.lower() == "bytedance":
        app_id = os.getenv("bytedance_app_id")
        api_key = os.getenv("bytedance_api_key")
        secret_key = os.getenv("bytedance_secret_key")
        
        if not all([app_id, api_key, secret_key]):
            logger.warning("字节跳动API凭证不完整，请在环境变量中设置 bytedance_app_id, bytedance_api_key, bytedance_secret_key")
        
        return {
            "app_id": app_id,
            "api_key": api_key,
            "secret_key": secret_key
        }
    
    elif provider.lower() == "xunfei":
        app_id = os.getenv("xunfei_app_id")
        api_key = os.getenv("xunfei_api_key")
        api_secret = os.getenv("xunfei_api_secret")
        
        if not all([app_id, api_key, api_secret]):
            logger.warning("科大讯飞API凭证不完整，请在环境变量中设置 xunfei_app_id, xunfei_api_key, xunfei_api_secret")
        
        return {
            "app_id": app_id,
            "api_key": api_key,
            "api_secret": api_secret
        }
    
    else:
        logger.error("不支持的供应商: %s", provider)
        return {}


def create_recognizer(provider, audio_file):
    """创建语音识别器实例"""
    logger.info("Creating speech recognizer for provider: %s", provider)
    
    # 从环境变量中获取凭证
    credentials = get_provider_credentials(provider)
    
    if provider.lower() == "baidu":
        # 使用百度离线语音识别
        logger.info("使用百度语音识别")
        return BaiduSpeechRecognizer(
            app_id=credentials.get("app_id", ""),
            api_key=credentials.get("api_key", ""),
            secret_key=credentials.get("secret_key", "")
        )
    elif provider.lower() == "bytedance":
        logger.info("使用字节跳动语音识别")
        return BytedanceSpeechRecognizer(
            app_id=credentials.get("app_id", ""),
            api_key=credentials.get("api_key", ""),
            secret_key=credentials.get("secret_key", ""),
            audio_file=audio_file
        )
    elif provider.lower() == "xunfei":
        logger.info("使用科大讯飞语音识别")
        return XunfeiOSTRecognizer(
            app_id=credentials.get("app_id", ""),
            api_key=credentials.get("api_key", ""),
            api_secret=credentials.get("api_secret", "")
        )
    else:
        raise ValueError(f"不支持的语音识别供应商: {provider}")


async def speech_to_text(arguments: dict | None) -> list[types.TextContent]:
    """将语音转换为文字并保存为Markdown文件。"""
    if not arguments or "audio_file" not in arguments:
        logger.error("Missing audio_file argument")
        raise ValueError("缺少必要参数: audio_file")

    audio_file = arguments["audio_file"]
    if not audio_file:
        error_msg = "音频文件路径不能为空"
        logger.error(error_msg)
        return [types.TextContent(type="text", text=error_msg)]

    # 获取供应商，默认为百度
    provider = arguments.get("provider", "baidu")  # 默认使用百度语音识别
    
    # 获取输出路径，如果未提供则使用默认路径
    output_path = arguments.get("output_path") or "~/.think-mcp-server/results"
    
    # 获取输出文件名，如果未提供则从音频文件名中提取
    output_filename = arguments.get("output_filename")
    
    # 展开路径中的 ~ 符号
    audio_file = os.path.expanduser(audio_file)
    output_path = os.path.expanduser(output_path)
    
    logger.info("Speech to text conversion starting")
    logger.info("Audio file: %s", audio_file)
    logger.info("Provider: %s", provider)
    logger.info("Output path: %s", output_path)
    
    try:
        # 确保音频文件存在（如果是本地文件）
        if not audio_file.startswith('http://') and not audio_file.startswith('https://'):
            if not os.path.exists(audio_file):
                error_msg = f"音频文件不存在: {audio_file}"
                logger.error(error_msg)
                return [types.TextContent(type="text", text=error_msg)]
        
        # 确保输出目录存在
        os.makedirs(output_path, exist_ok=True)
        logger.debug("Output directory created/verified: %s", output_path)
        
        # 如果未提供输出文件名，从音频文件中提取
        if not output_filename:
            audio_name = os.path.basename(audio_file).split('?')[0]  # 移除URL参数
            audio_name = os.path.splitext(audio_name)[0]
            output_filename = f"{audio_name}.md"
        elif not output_filename.endswith(".md"):
            # 确保文件名有正确的扩展名
            output_filename = f"{output_filename}.md"
        
        output_file = os.path.join(output_path, output_filename)
        logger.info("Output file will be: %s", output_file)
        
        # 创建语音识别器
        recognizer = create_recognizer(provider, audio_file)
        
        # 执行语音识别
        logger.info("Starting speech recognition")
        if provider.lower() == "xunfei":
            text_result = await recognizer.recognize(audio_file)
        else:
            text_result = await recognizer.recognize(audio_file)
        logger.info("Speech recognition completed")
        
        # 生成Markdown内容
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        markdown_content = f"""---
title: 语音转文字结果
audio_file: {audio_file}
provider: {provider}
date: {current_time}
---

# 语音转文字结果

**音频文件**: {os.path.basename(audio_file)}  
**识别时间**: {current_time}  
**识别引擎**: {provider}  

## 识别文本

{text_result}
"""
        
        # 写入Markdown文件
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        
        logger.info("Markdown file written successfully: %s", output_file)
        
        return [types.TextContent(
            type="text", 
            text=f"语音转文字成功!\n文件路径: {output_file}\n\n## 识别文本预览\n\n{text_result[:500]}{'...' if len(text_result) > 500 else ''}"
        )]
        
    except Exception as e:
        error_msg = f"语音转文字时出错: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return [types.TextContent(type="text", text=error_msg)]
