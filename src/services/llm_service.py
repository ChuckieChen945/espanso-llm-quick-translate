"""LLM服务模块.

负责与AI模型交互，处理翻译请求。
"""

import asyncio
from pathlib import Path
from string import Template

from openai import OpenAI

from config import ConfigManager


class LLMService:
    """LLM服务类.

    负责与AI模型交互，处理翻译请求。
    """

    def __init__(self, config: ConfigManager) -> None:
        """初始化LLM服务.

        Args:
            config: 配置管理器
        """
        self.config = config
        self.client = OpenAI(
            api_key=config.api_key,
            base_url=config.base_url,
        )
        self._system_prompt: str | None = None

    def _load_system_prompt(self) -> str:
        """加载系统提示.

        Returns
        -------
            系统提示内容
        """
        if self._system_prompt is None:
            prompt_file = Path(self.config.system_prompt_file)
            if not prompt_file.exists():
                msg = f"系统提示文件不存在: {prompt_file}"
                raise FileNotFoundError(msg)

            with Path.open(prompt_file, encoding="utf-8") as f:
                self._system_prompt = f.read()

        return self._system_prompt

    def translate(self, text: str) -> str:
        """翻译文本.

        Args:
            text: 要翻译的文本

        Returns
        -------
            翻译结果
        """
        try:
            system_prompt = self._load_system_prompt()
            template = Template(system_prompt)

            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {
                        "role": "system",
                        "content": template.substitute(TARGET_LANGUAGE=self.config.target_language),
                    },
                    {
                        "role": "user",
                        "content": text,
                    },
                ],
                stream=False,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            return f"❌ 翻译失败: {e!s}"

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
