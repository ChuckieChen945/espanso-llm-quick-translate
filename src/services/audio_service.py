"""音频服务模块.

处理TTS生成和音频播放。
"""

from pathlib import Path

from edge_tts import Communicate
from playsound import playsound

from config import ConfigManager


class AudioService:
    """音频服务类.

    处理TTS生成和音频播放。
    """

    def __init__(self, config: ConfigManager) -> None:
        """初始化音频服务.

        Args:
            config: 配置管理器
        """
        self.config = config
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
        """
        if file_path is None:
            file_path = self.config.audio_file_path

        if sound_name is None:
            sound_name = self.config.sound_name

        communicate = Communicate(text, sound_name)
        await communicate.save(file_path)

        self._last_audio_file = file_path
        return file_path

    # TODO： Boolean-typed positional argument in function definition (RuffFBT001)
    def play_audio(self, filepath: str, block: bool = True) -> None:
        """播放音频文件.

        Args:
            filepath: 音频文件路径
            block: 是否阻塞播放
        """
        if not Path(filepath).exists():
            msg = f"音频文件不存在: {filepath}"
            raise FileNotFoundError(msg)

        playsound(filepath, block=block)

    # TODO： Boolean-typed positional argument in function definition (RuffFBT001)
    def play_last_audio(self, block: bool = True) -> None:
        """播放最后生成的音频.

        Args:
            block: 是否阻塞播放
        """
        if self._last_audio_file is None:
            msg = "没有可播放的音频文件"
            raise ValueError(msg)

        self.play_audio(self._last_audio_file, block)

    @property
    def last_audio_file(self) -> str | None:
        """获取最后生成的音频文件路径."""
        return self._last_audio_file
