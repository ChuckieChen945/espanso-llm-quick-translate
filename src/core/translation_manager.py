"""翻译管理器模块.

协调各个服务，管理翻译流程。立即返回翻译结果，其余工作异步执行。
"""

import concurrent.futures
import subprocess
import sys
import time
from pathlib import Path

from src.config import ConfigManager
from src.services import AudioService, DiffService, LLMService
from src.utils import get_logger


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
        """翻译文本并立即返回结果，并异步生成音频和diff."""
        start_time = time.time()
        self.logger.info(f"开始翻译文本: {text[:50]}{'...' if len(text) > 50 else ''}")
        try:
            # 立即调用LLM API翻译
            translated = self.llm_service.translate(text)
            translation_time = time.time() - start_time
            self.logger.info(f"翻译完成，耗时: {translation_time:.2f}秒")
            self.logger.info(f"翻译结果: {translated[:50]}{'...' if len(translated) > 50 else ''}")
            # 启动音频生成子进程
            self._start_audio_process(translated)
            # 启动diff生成子进程
            self._start_diff_process(text, translated)
        except Exception as e:
            self.logger.error(f"翻译失败: {e}", exc_info=True)
            return f"❌ 翻译失败: {e}"
        else:
            return translated

    def _start_audio_process(self, translated_text: str) -> None:
        """启动音频生成子进程."""
        script_path = Path(__file__).parent.parent / "subprocesses/generate_audio.py"
        subprocess.Popen(
            [sys.executable, script_path, translated_text],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True,  # 创建新的会话组
        )

    def _start_diff_process(self, original_text: str, translated_text: str) -> None:
        """启动diff生成子进程."""
        script_path = Path(__file__).parent.parent / "subprocesses/generate_diff.py"
        subprocess.Popen(
            [sys.executable, script_path, original_text, translated_text],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True,  # 创建新的会话组
        )

    def play_last_audio(self) -> None:
        """手动播放音频."""
        try:
            self.logger.info("手动播放音频")
            self.audio_service.play_last_audio()
            self.logger.info("音频播放完成")
        except Exception as e:
            self.logger.error(f"音频播放失败: {e}", exc_info=True)

    @property
    def last_audio_file(self) -> str | None:
        """获取最后一个音频文件路径."""
        return self.audio_service.last_audio_file
