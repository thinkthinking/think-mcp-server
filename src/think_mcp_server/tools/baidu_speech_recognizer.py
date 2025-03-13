#!/usr/bin/python3
# -*- coding:utf-8 -*-
"""百度离线语音识别模块。"""

import os
import json
import time
import sys
import base64
import hashlib
from urllib.request import urlopen, Request
from urllib.error import URLError
from urllib.parse import urlencode
import ssl
import requests
from pathlib import Path
from think_llm_client.utils.logger import logging

# 获取模块的日志记录器
logger = logging.getLogger("think-mcp-server")

# 禁用SSL证书验证
ssl._create_default_https_context = ssl._create_unverified_context


class DemoError(Exception):
    """百度API错误类"""
    pass


class BaiduSpeechRecognizer:
    """百度离线语音识别实现，适用于长音频文件。"""
    
    def __init__(self, app_id, api_key, secret_key):
        """初始化百度离线语音识别参数。
        
        Args:
            app_id: 百度应用ID
            api_key: 百度API密钥
            secret_key: 百度API密钥
        """
        self.API_KEY = api_key
        self.SECRET_KEY = secret_key
        self.APP_ID = app_id
        
        # 百度语音识别API地址
        self.TOKEN_URL = 'https://openapi.baidu.com/oauth/2.0/token'
        self.CREATE_URL = 'https://aip.baidubce.com/rpc/2.0/aasr/v1/create'
        self.QUERY_URL = 'https://aip.baidubce.com/rpc/2.0/aasr/v1/query'
        
        # 设置权限范围
        self.SCOPE = 'brain_asr_async'  # 有此scope表示有asr能力，没有请在网页里勾选
        
    def fetch_token(self):
        """获取百度API访问token。"""
        params = {
            'grant_type': 'client_credentials',
            'client_id': self.API_KEY,
            'client_secret': self.SECRET_KEY
        }
        
        post_data = urlencode(params)
        post_data = post_data.encode('utf-8')
        req = Request(self.TOKEN_URL, post_data)
        
        try:
            f = urlopen(req)
            result_str = f.read()
            result_str = result_str.decode()
            
            logger.debug("Token响应: %s", result_str)
            result = json.loads(result_str)
            
            if ('access_token' in result.keys() and 'scope' in result.keys()):
                if not self.SCOPE in result['scope'].split(' '):
                    error_msg = 'scope权限范围不正确'
                    logger.error(error_msg)
                    raise DemoError(error_msg)
                
                logger.info("获取token成功，有效期: %s秒", result['expires_in'])
                return result['access_token']
            else:
                error_msg = 'API_KEY或SECRET_KEY不正确: access_token或scope未在响应中找到'
                logger.error(error_msg)
                raise DemoError(error_msg)
        except URLError as err:
            error_msg = f'获取token失败，HTTP状态码: {err.code}'
            logger.error(error_msg)
            raise DemoError(error_msg)
        except Exception as e:
            error_msg = f'获取token异常: {str(e)}'
            logger.error(error_msg)
            raise
    
    def get_audio_url(self, audio_file):
        """获取音频文件的URL。
        
        如果音频文件是URL（以http或https开头），则直接返回；
        否则，将其视为本地文件路径，需要上传到云存储获取URL。
        
        Args:
            audio_file: 音频文件路径或URL
            
        Returns:
            可访问的音频URL
        """
        if audio_file.startswith('http://') or audio_file.startswith('https://'):
            logger.info("检测到音频文件是URL: %s", audio_file)
            return audio_file
        else:
            # 这里应该实现上传到云存储的逻辑，返回可访问的URL
            # 由于这超出了本示例的范围，这里仅返回一个假的URL
            logger.warning("音频文件不是URL，需要上传到云存储才能使用百度语音识别")
            logger.warning("请提供可公开访问的音频URL，例如百度云BOS链接")
            raise ValueError("百度语音识别需要可公开访问的音频URL，请提供BOS链接而非本地文件路径")
    
    def create_task(self, audio_url, audio_format="mp3", pid=80001, rate=16000):
        """创建语音识别任务。
        
        Args:
            audio_url: 音频文件URL，需要可公开访问
            audio_format: 音频格式，支持mp3、wav、pcm、m4a、amr
            pid: 语言类型，80001为中文语音近场识别模型极速版，80006为中文音视频字幕模型，1737为英文模型
            rate: 采样率，固定值16000
            
        Returns:
            任务ID
        """
        logger.info("创建语音识别任务...")
        
        # 获取访问token
        token = self.fetch_token()
        
        # 请求体
        body = {
            "speech_url": audio_url,
            "format": audio_format,
            "pid": pid,
            "rate": rate
        }
        
        # 请求头
        headers = {'content-type': "application/json"}
        
        # 请求参数
        params = {"access_token": token}
        
        try:
            # 发送请求
            response = requests.post(
                self.CREATE_URL,
                params=params,
                data=json.dumps(body),
                headers=headers
            )
            
            # 解析响应
            result = response.json()
            logger.debug("创建任务响应: %s", json.dumps(result, ensure_ascii=False))
            
            # 检查是否成功
            if "task_id" in result:
                task_id = result["task_id"]
                logger.info("创建任务成功，任务ID: %s", task_id)
                return task_id
            else:
                error_msg = f"创建任务失败: {result}"
                logger.error(error_msg)
                raise Exception(error_msg)
        except Exception as e:
            error_msg = f"创建任务异常: {str(e)}"
            logger.error(error_msg)
            raise
    
    def query_task(self, task_id):
        """查询语音识别任务结果。
        
        Args:
            task_id: 任务ID
            
        Returns:
            识别结果
        """
        logger.info("查询任务结果，任务ID: %s", task_id)
        
        # 获取访问token
        token = self.fetch_token()
        
        # 请求体
        body = {
            "task_ids": [task_id]
        }
        
        # 请求头
        headers = {'content-type': "application/json"}
        
        # 请求参数
        params = {"access_token": token}
        
        try:
            # 发送请求
            response = requests.post(
                self.QUERY_URL,
                params=params,
                data=json.dumps(body),
                headers=headers
            )
            
            # 解析响应
            result = response.json()
            logger.debug("查询任务响应: %s", json.dumps(result, ensure_ascii=False))
            
            return result
        except Exception as e:
            error_msg = f"查询任务异常: {str(e)}"
            logger.error(error_msg)
            raise
    
    def get_audio_format(self, audio_file):
        """根据音频文件扩展名获取格式。"""
        # 如果是URL，从URL中提取扩展名
        if audio_file.startswith('http://') or audio_file.startswith('https://'):
            # 移除URL参数
            url_path = audio_file.split('?')[0]
            ext = os.path.splitext(url_path)[1].lower()
        else:
            ext = os.path.splitext(audio_file)[1].lower()
            
        format_map = {
            '.mp3': 'mp3',
            '.wav': 'wav',
            '.pcm': 'pcm',
            '.m4a': 'm4a',
            '.amr': 'amr'
        }
        return format_map.get(ext, 'mp3')  # 默认返回mp3
    
    def parse_result(self, result):
        """解析识别结果。"""
        if "tasks_info" not in result or not result["tasks_info"]:
            logger.warning("未找到任务信息")
            return ""
        
        task_info = result["tasks_info"][0]
        task_status = task_info.get("task_status", "")
        
        if task_status == "Success":
            task_result = task_info.get("task_result", {})
            result_text = "".join(task_result.get("result", []))
            logger.info("识别成功，文本长度: %d", len(result_text))
            return result_text
        elif task_status == "Running":
            logger.info("任务仍在处理中")
            return ""
        elif task_status == "Failure":
            task_result = task_info.get("task_result", {})
            err_no = task_result.get("err_no", 0)
            err_msg = task_result.get("err_msg", "未知错误")
            logger.error("任务失败，错误码: %s, 错误信息: %s", err_no, err_msg)
            return f"识别失败: {err_msg}"
        else:
            logger.warning("未知任务状态: %s", task_status)
            return ""
    
    async def recognize(self, audio_file):
        """执行离线语音识别。
        
        Args:
            audio_file: 音频文件路径或URL
            
        Returns:
            识别结果文本
        """
        logger.info("开始百度离线语音识别，音频文件：%s", audio_file)
        
        try:
            # 1. 获取音频URL
            audio_url = self.get_audio_url(audio_file)
            logger.info("音频文件URL: %s", audio_url)
            
            # 2. 获取音频格式
            audio_format = self.get_audio_format(audio_file)
            logger.info("音频格式: %s", audio_format)
            
            # 3. 创建识别任务
            task_id = self.create_task(audio_url, audio_format)
            
            # 4. 查询识别结果
            max_retry = 100
            retry_count = 0
            
            while retry_count < max_retry:
                # 查询任务结果
                result = self.query_task(task_id)
                
                # 检查任务是否完成
                if "tasks_info" in result and result["tasks_info"]:
                    task_info = result["tasks_info"][0]
                    task_status = task_info.get("task_status", "")
                    
                    if task_status == "Success":
                        # 任务成功完成
                        logger.info("识别任务成功完成")
                        return self.parse_result(result)
                    elif task_status == "Failure":
                        # 任务失败
                        error_msg = f"识别任务失败: {task_info}"
                        logger.error(error_msg)
                        raise Exception(error_msg)
                    elif task_status == "Running":
                        # 任务仍在处理中，等待后继续查询
                        logger.info("任务正在处理中，等待...")
                        time.sleep(5)
                    else:
                        # 未知状态
                        logger.warning("未知任务状态: %s，继续等待...", task_status)
                        time.sleep(5)
                else:
                    # 查询结果异常
                    logger.warning("查询结果异常: %s，继续等待...", result)
                    time.sleep(5)
                
                retry_count += 1
            
            # 超过最大重试次数
            error_msg = "识别超时，超过最大重试次数"
            logger.error(error_msg)
            raise Exception(error_msg)
            
        except Exception as e:
            logger.error("百度离线语音识别失败: %s", str(e), exc_info=True)
            raise
