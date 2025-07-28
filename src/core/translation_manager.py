"""翻译管理器模块.

协调各个服务，管理翻译流程。立即返回翻译结果，其余工作异步执行。
"""

import asyncio
import threading
import time

from config import ConfigManager
from services import AudioService, DiffService, LLMService
from utils import get_logger


class TranslationManager:
    """翻译管理器类.

    协调各个服务，管理翻译流程。优化为立即返回翻译结果，其余工作异步执行。
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
        self.logger = get_logger("TranslationManager")
        self._background_tasks: list[threading.Thread] = []

    def translate_text(self, text: str) -> str:
        """翻译文本并立即返回结果.

        立即调用LLM API翻译文本，返回结果给espanso。
        其余工作（音频生成、diff生成、自动播放）在后台异步执行。

        Args:
            text: 要翻译的文本

        Returns
        -------
            翻译结果
        """
        start_time = time.time()
        self.logger.info(f"开始翻译文本: {text[:50]}{'...' if len(text) > 50 else ''}")

        try:
            # 立即调用LLM API翻译
            translated = self.llm_service.translate(text)

            translation_time = time.time() - start_time
            self.logger.info(f"翻译完成，耗时: {translation_time:.2f}秒")
            self.logger.info(f"翻译结果: {translated[:50]}{'...' if len(translated) > 50 else ''}")

            # TODO: 修正后台任务不会被执行的 Bug

            # 在后台异步执行其余工作
            self._start_background_tasks(text, translated)

        except Exception as e:
            self.logger.error(f"翻译失败: {e}", exc_info=True)
            return f"❌ 翻译失败: {e}"
        else:
            return translated

    def _start_background_tasks(self, original_text: str, translated_text: str) -> None:
        """启动后台任务.

        Args:
            original_text: 原始文本
            translated_text: 翻译文本
        """
        # 创建后台线程执行异步任务
        background_thread = threading.Thread(
            target=self._run_background_tasks,
            args=(original_text, translated_text),
            daemon=True,
        )
        background_thread.start()
        self._background_tasks.append(background_thread)

    def _run_background_tasks(self, original_text: str, translated_text: str) -> None:
        """运行后台任务.

        Args:
            original_text: 原始文本
            translated_text: 翻译文本
        """
        try:
            # 创建新的事件循环用于后台任务
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # 运行异步任务
            loop.run_until_complete(self._execute_background_tasks(original_text, translated_text))

        except Exception as e:
            self.logger.error(f"后台任务执行失败: {e}", exc_info=True)
        finally:
            loop.close()

    async def _execute_background_tasks(self, original_text: str, translated_text: str) -> None:
        """执行后台异步任务.

        Args:
            original_text: 原始文本
            translated_text: 翻译文本
        """
        start_time = time.time()
        self.logger.info("开始执行后台任务")

        try:
            # 并行执行diff生成和音频生成
            diff_task = asyncio.create_task(
                self._generate_diff_async(original_text, translated_text),
            )
            audio_task = asyncio.create_task(self._generate_audio_async(translated_text))

            # 等待所有任务完成
            await asyncio.gather(diff_task, audio_task)

            # 如果配置了自动播放，播放音频
            if self.config.auto_play:
                await asyncio.create_task(self._play_audio_async())

            total_time = time.time() - start_time
            self.logger.info(f"后台任务完成，总耗时: {total_time:.2f}秒")

        except Exception as e:
            self.logger.error(f"后台任务执行失败: {e}", exc_info=True)

    async def _generate_diff_async(self, original_text: str, translated_text: str) -> None:
        """异步生成diff.

        Args:
            original_text: 原始文本
            translated_text: 翻译文本
        """
        try:
            start_time = time.time()
            self.logger.info("开始生成diff")

            # 在线程池中运行同步的diff生成
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self.diff_service.generate_and_write_diff,
                original_text,
                translated_text,
            )

            diff_time = time.time() - start_time
            self.logger.info(f"diff生成完成，耗时: {diff_time:.2f}秒")

        except Exception as e:
            self.logger.error(f"diff生成失败: {e}", exc_info=True)

    async def _generate_audio_async(self, text: str) -> None:
        """异步生成音频.

        Args:
            text: 要转换的文本
        """
        try:
            start_time = time.time()
            self.logger.info("开始生成音频")

            await self.audio_service.generate_tts_audio(text)

            audio_time = time.time() - start_time
            self.logger.info(f"音频生成完成，耗时: {audio_time:.2f}秒")

        except Exception as e:
            self.logger.error(f"音频生成失败: {e}", exc_info=True)

    async def _play_audio_async(self) -> None:
        """异步播放音频."""
        try:
            start_time = time.time()
            self.logger.info("开始播放音频")

            # 在线程池中运行同步的音频播放
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self.audio_service.play_last_audio,
                False,  # 非阻塞播放
            )

            play_time = time.time() - start_time
            self.logger.info(f"音频播放完成，耗时: {play_time:.2f}秒")

        except Exception as e:
            self.logger.error(f"音频播放失败: {e}", exc_info=True)

    def play_last_audio(self) -> None:
        """播放最后生成的音频."""
        try:
            self.logger.info("手动播放音频")
            self.audio_service.play_last_audio()
            self.logger.info("音频播放完成")
        except Exception as e:
            self.logger.error(f"音频播放失败: {e}", exc_info=True)
            print(f"❌ 音频播放失败: {e}")

    @property
    def last_audio_file(self) -> str | None:
        """获取最后生成的音频文件路径."""
        return self.audio_service.last_audio_file

    def wait_for_background_tasks(self) -> None:
        """等待所有后台任务完成."""
        for task in self._background_tasks:
            if task.is_alive():
                task.join()
        self._background_tasks.clear()
