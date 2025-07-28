"""LLM服务模块.

负责与AI模型交互，处理翻译请求。优化为支持详细的日志记录和错误处理。
支持代理配置。
"""

import asyncio
import time
from pathlib import Path
from string import Template

import httpx
from openai import OpenAI

from config import ConfigManager
from utils import get_logger


class LLMService:
    """LLM服务类.

    负责与AI模型交互，处理翻译请求。支持详细的日志记录和错误处理。
    支持代理配置。
    """

    def __init__(self, config: ConfigManager) -> None:
        """初始化LLM服务.

        Args:
            config: 配置管理器
        """
        self.config = config
        self.logger = get_logger("LLMService")
        self._system_prompt: str | None = None

        # 构建客户端配置
        client_kwargs = {
            "api_key": config.api_key,
            "base_url": config.base_url,
        }

        # 添加代理配置（如果配置了）
        if hasattr(config, "proxy") and config.proxy:
            client_kwargs["http_client"] = self._create_proxy_client(config.proxy)
            self.logger.info(f"使用代理: {config.proxy}")

        self.client = OpenAI(**client_kwargs)

    def _create_proxy_client(self, proxy_url: str) -> httpx.Client | None:
        """创建代理客户端.

        Args:
            proxy_url: 代理URL

        Returns
        -------
            配置了代理的HTTP客户端
        """
        try:
            return httpx.Client(
                proxies=proxy_url,
                timeout=30.0,
            )
        except ImportError:
            self.logger.warning("httpx未安装，无法使用代理功能")
            return None

    def _load_system_prompt(self) -> str:
        """加载系统提示.

        Returns
        -------
            系统提示内容

        Raises
        ------
            FileNotFoundError: 系统提示文件不存在
        """
        if self._system_prompt is None:
            prompt_file = Path(self.config.system_prompt_file)
            if not prompt_file.exists():
                msg = f"系统提示文件不存在: {prompt_file}"
                self.logger.error(msg)
                raise FileNotFoundError(msg)

            try:
                with Path.open(prompt_file, encoding="utf-8") as f:
                    self._system_prompt = f.read()
                self.logger.debug(f"成功加载系统提示文件: {prompt_file}")
            except Exception as e:
                msg = f"读取系统提示文件失败: {e}"
                self.logger.error(msg)
                raise FileNotFoundError(msg) from e

        return self._system_prompt

    def translate(self, text: str) -> str:
        """翻译文本.

        Args:
            text: 要翻译的文本

        Returns
        -------
            翻译结果

        Raises
        ------
            Exception: 翻译过程中的任何错误
        """
        start_time = time.time()
        self.logger.info(f"开始调用LLM API翻译文本: {text[:50]}{'...' if len(text) > 50 else ''}")

        try:
            # 加载系统提示
            system_prompt = self._load_system_prompt()
            template = Template(system_prompt)
            formatted_prompt = template.substitute(TARGET_LANGUAGE=self.config.target_language)

            self.logger.debug(f"使用模型: {self.config.model}")
            self.logger.debug(f"目标语言: {self.config.target_language}")

            # 调用LLM API
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {
                        "role": "system",
                        "content": formatted_prompt,
                    },
                    {
                        "role": "user",
                        "content": text,
                    },
                ],
                stream=False,
                timeout=30,  # 30秒超时
            )

            translated_text = response.choices[0].message.content.strip()

            api_time = time.time() - start_time
            self.logger.info(f"LLM API调用成功，耗时: {api_time:.2f}秒")
            self.logger.debug(
                f"翻译结果: {translated_text[:100]}{'...' if len(translated_text) > 100 else ''}",
            )

        except Exception as e:
            api_time = time.time() - start_time
            self.logger.error(f"LLM API调用失败，耗时: {api_time:.2f}秒，错误: {e}", exc_info=True)
            msg = f"翻译失败: {e}"
            raise Exception(msg) from e
        else:
            return translated_text

    async def translate_async(self, text: str) -> str:
        """异步翻译文本.

        Args:
            text: 要翻译的文本

        Returns
        -------
            翻译结果
        """
        # 在线程池中运行同步方法
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.translate, text)

    def test_connection(self) -> bool:
        """测试LLM API连接.

        Returns
        -------
            连接是否成功
        """
        try:
            self.logger.info("测试LLM API连接")

            # 发送一个简单的测试请求
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "user", "content": "Hello"},
                ],
                max_tokens=10,
                timeout=10,  # 10秒超时
            )

            self.logger.info("LLM API连接测试成功")

        except Exception as e:
            self.logger.error(f"LLM API连接测试失败: {e}", exc_info=True)
            return False
        else:
            return True
