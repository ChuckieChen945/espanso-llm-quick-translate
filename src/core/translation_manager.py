"""翻译管理器模块.

协调各个服务，管理翻译流程。
"""

import asyncio
from typing import Any

from config import ConfigManager
from services import AudioService, DiffService, LLMService


class TranslationManager:
    """翻译管理器类.

    协调各个服务，管理翻译流程。
    """

    def __init__(self, config: ConfigManager) -> None:
        """初始化翻译管理器.

        Args:
            config: 配置管理器
        """
        self.config = config
        self.llm_service = LLMService(config)
        self.audio_service = AudioService(config)
        self.diff_service = DiffService(config)
        self._audio_task: asyncio.Task[Any] | None = None

    def translate_text(self, text: str) -> str:
        """翻译文本.

        Args:
            text: 要翻译的文本

        Returns
        -------
            翻译结果
        """
        # 翻译文本
        translated = self.llm_service.translate(text)

        # TODO：立即返回生成的文本交给 espanso 处理，然后剩下的工作全部异步完成

        # 生成diff并写入文件
        self.diff_service.generate_and_write_diff(text, translated)

        # 异步生成音频
        self._audio_task = asyncio.create_task(self._generate_audio_async(translated))

        return translated

    async def translate_text_async(self, text: str) -> str:
        """异步翻译文本.

        Args:
            text: 要翻译的文本

        Returns
        -------
            翻译结果
        """
        # 异步翻译文本
        translated = await self.llm_service.translate_async(text)

        # 生成diff并写入文件
        self.diff_service.generate_and_write_diff(text, translated)

        # 生成音频
        await self._generate_audio_async(translated)

        return translated

    async def _generate_audio_async(self, text: str) -> None:
        """异步生成音频.

        Args:
            text: 要转换的文本
        """
        try:
            await self.audio_service.generate_tts_audio(text)

            # 如果配置了自动播放，则播放音频
            if self.config.auto_play:
                self.audio_service.play_last_audio(block=False)

        except Exception as e:
            print(f"❌ 音频生成失败: {e}")

    def play_last_audio(self) -> None:
        """播放最后生成的音频."""
        try:
            self.audio_service.play_last_audio()
        except Exception as e:
            print(f"❌ 音频播放失败: {e}")

    @property
    def last_audio_file(self) -> str | None:
        """获取最后生成的音频文件路径."""
        return self.audio_service.last_audio_file

    def wait_for_audio_completion(self) -> None:
        """等待音频生成完成."""
        if self._audio_task and not self._audio_task.done():
            try:
                # 在同步环境中等待异步任务
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # 如果事件循环正在运行，使用线程池
                    import concurrent.futures

                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, self._audio_task)
                        future.result()
                else:
                    loop.run_until_complete(self._audio_task)
            except Exception as e:
                print(f"❌ 等待音频生成完成时出错: {e}")
