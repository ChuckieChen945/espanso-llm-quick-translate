"""翻译管理器模块.

协调各个服务，管理翻译流程。立即返回翻译结果，其余工作异步执行。
"""

import asyncio
import concurrent.futures
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
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=3)
        self._background_tasks: list[concurrent.futures.Future] = []

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
        try:
            # 使用线程池执行后台任务
            future = self._executor.submit(
                self._run_background_tasks_sync,
                original_text,
                translated_text,
            )
            self._background_tasks.append(future)

            # 添加回调处理异常
            future.add_done_callback(self._handle_background_task_completion)

            self.logger.info("后台任务已启动")

        except Exception as e:
            self.logger.error(f"启动后台任务失败: {e}", exc_info=True)

    def _run_background_tasks_sync(self, original_text: str, translated_text: str) -> None:
        """同步运行后台任务.

        Args:
            original_text: 原始文本
            translated_text: 翻译文本
        """
        start_time = time.time()
        self.logger.info("开始执行后台任务")

        try:
            # 并行执行diff生成和音频生成
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                # 提交diff生成任务
                diff_future = executor.submit(
                    self.diff_service.generate_and_write_diff,
                    original_text,
                    translated_text,
                )

                # 提交音频生成任务
                audio_future = executor.submit(
                    self._generate_audio_sync,
                    translated_text,
                )

                # 等待diff生成完成
                diff_future.result()
                self.logger.info("diff生成完成")

                # 等待音频生成完成
                audio_future.result()
                self.logger.info("音频生成完成")

                # 如果配置了自动播放，播放音频
                if self.config.auto_play:
                    self._play_audio_sync()
                    self.logger.info("自动播放音频完成")

            total_time = time.time() - start_time
            self.logger.info(f"后台任务完成，总耗时: {total_time:.2f}秒")

        except Exception as e:
            total_time = time.time() - start_time
            self.logger.error(
                f"后台任务执行失败，总耗时: {total_time:.2f}秒，错误: {e}",
                exc_info=True,
            )

    def _generate_audio_sync(self, text: str) -> None:
        """同步生成音频.

        Args:
            text: 要转换的文本
        """
        try:
            start_time = time.time()
            self.logger.info("开始生成音频")

            # 创建新的事件循环用于异步操作
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                # 运行异步音频生成
                loop.run_until_complete(self.audio_service.generate_tts_audio(text))

                audio_time = time.time() - start_time
                self.logger.info(f"音频生成完成，耗时: {audio_time:.2f}秒")

            finally:
                loop.close()

        except Exception as e:
            self.logger.error(f"音频生成失败: {e}", exc_info=True)

    def _play_audio_sync(self) -> None:
        """同步播放音频."""
        try:
            start_time = time.time()
            self.logger.info("开始播放音频")

            self.audio_service.play_last_audio(block=False)

            play_time = time.time() - start_time
            self.logger.info(f"音频播放完成，耗时: {play_time:.2f}秒")

        except Exception as e:
            self.logger.error(f"音频播放失败: {e}", exc_info=True)

    def _handle_background_task_completion(self, future: concurrent.futures.Future) -> None:
        """处理后台任务完成回调.

        Args:
            future: 完成的任务
        """
        try:
            # 获取任务结果（如果有异常会抛出）
            future.result()
            self.logger.debug("后台任务成功完成")
        except Exception as e:
            self.logger.error(f"后台任务执行异常: {e}", exc_info=True)
        finally:
            # 从任务列表中移除已完成的任务
            if future in self._background_tasks:
                self._background_tasks.remove(future)

    def play_last_audio(self) -> None:
        """播放最后生成的音频."""
        try:
            self.logger.info("手动播放音频")
            self.audio_service.play_last_audio()
            self.logger.info("音频播放完成")
        except Exception as e:
            self.logger.error(f"音频播放失败: {e}", exc_info=True)
            # print(f"❌ 音频播放失败: {e}")

    @property
    def last_audio_file(self) -> str | None:
        """获取最后生成的音频文件路径."""
        return self.audio_service.last_audio_file

    def wait_for_background_tasks(self) -> None:
        """等待所有后台任务完成."""
        for task in self._background_tasks[:]:  # 创建副本避免修改迭代列表
            if not task.done():
                try:
                    task.result(timeout=30)  # 30秒超时
                except concurrent.futures.TimeoutError:
                    self.logger.warning("后台任务超时")
                except Exception as e:
                    self.logger.error(f"后台任务异常: {e}")

        self._background_tasks.clear()

    def __del__(self) -> None:
        """析构函数，确保资源清理."""
        try:
            self._executor.shutdown(wait=True)
        except Exception:
            pass
