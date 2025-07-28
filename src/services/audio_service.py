"""音频服务模块.

处理TTS生成和音频播放。支持详细的日志记录和错误处理。
"""

import time
from pathlib import Path

from edge_tts import Communicate
from playsound import playsound

from config import ConfigManager
from utils import get_logger


class AudioService:
    """音频服务类.

    处理TTS生成和音频播放。支持详细的日志记录和错误处理。
    """

    def __init__(self, config: ConfigManager) -> None:
        """初始化音频服务.

        Args:
            config: 配置管理器
        """
        self.config = config
        self.logger = get_logger("AudioService")
        self._last_audio_file: str | None = None

    async def generate_tts_audio(
        self,
        text: str,
        file_path: str | None = None,
        sound_name: str | None = None,
    ) -> str:
        """生成TTS音频.

        Args:
            text: 要转换的文本
            file_path: 输出文件名
            sound_name: 语音名称

        Returns
        -------
            生成的音频文件路径

        Raises
        ------
            Exception: 音频生成过程中的任何错误
        """
        start_time = time.time()

        if file_path is None:
            file_path = self.config.audio_file_path

        if sound_name is None:
            sound_name = self.config.sound_name

        self.logger.info(f"开始生成TTS音频，文本长度: {len(text)}字符")
        self.logger.debug(f"使用语音: {sound_name}")
        self.logger.debug(f"输出文件: {file_path}")

        try:
            # 确保输出目录存在
            output_path = Path(file_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # 生成音频
            communicate = Communicate(text, sound_name)
            # FIXME: cannot schedule new futures after interpreter shutdown
            await communicate.save(file_path)

            # 验证文件是否生成成功
            if not Path(file_path).exists():
                msg = f"音频文件生成失败: {file_path}"
                # TODO: Abstract `raise` to an inner function
                raise Exception(msg)

            self._last_audio_file = file_path

            tts_time = time.time() - start_time
            file_size = Path(file_path).stat().st_size / 1024  # KB
            self.logger.info(
                f"TTS音频生成成功，耗时: {tts_time:.2f}秒，文件大小: {file_size:.1f}KB",
            )

        except Exception as e:
            tts_time = time.time() - start_time
            self.logger.error(f"TTS音频生成失败，耗时: {tts_time:.2f}秒，错误: {e}", exc_info=True)
            raise Exception(f"音频生成失败: {e}") from e
        else:
            return file_path

    def play_audio(self, filepath: str, *, block: bool = True) -> None:
        """播放音频文件.

        Args:
            filepath: 音频文件路径
            block: 是否阻塞播放

        Raises
        ------
            FileNotFoundError: 音频文件不存在
            Exception: 播放过程中的任何错误
        """
        start_time = time.time()
        self.logger.info(f"开始播放音频文件: {filepath}")
        self.logger.debug(f"阻塞播放: {block}")

        if not Path(filepath).exists():
            msg = f"音频文件不存在: {filepath}"
            self.logger.error(msg)
            raise FileNotFoundError(msg)

        try:
            # 获取文件信息
            file_size = Path(filepath).stat().st_size / 1024  # KB
            self.logger.debug(f"音频文件大小: {file_size:.1f}KB")

            # 播放音频
            playsound(filepath, block=block)

            play_time = time.time() - start_time
            self.logger.info(f"音频播放完成，耗时: {play_time:.2f}秒")

        except Exception as e:
            play_time = time.time() - start_time
            self.logger.error(f"音频播放失败，耗时: {play_time:.2f}秒，错误: {e}", exc_info=True)
            raise Exception(f"音频播放失败: {e}") from e

    def play_last_audio(self, *, block: bool = True) -> None:
        """播放最后生成的音频.

        Args:
            block: 是否阻塞播放

        Raises
        ------
            ValueError: 没有可播放的音频文件
        """
        if self._last_audio_file is None:
            msg = "没有可播放的音频文件"
            self.logger.error(msg)
            raise ValueError(msg)

        self.play_audio(self._last_audio_file, block=block)

    @property
    def last_audio_file(self) -> str | None:
        """获取最后生成的音频文件路径."""
        return self._last_audio_file

    def test_tts_connection(self) -> bool:
        """测试TTS服务连接.

        Returns
        -------
            连接是否成功
        """
        try:
            self.logger.info("测试TTS服务连接")

            # 尝试创建一个简单的Communicate对象
            communicate = Communicate("Test", self.config.sound_name)

            self.logger.info("TTS服务连接测试成功")

        except Exception as e:
            self.logger.error(f"TTS服务连接测试失败: {e}", exc_info=True)
            return False
        else:
            return True
