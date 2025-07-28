"""配置管理模块.

统一管理项目配置，支持从JSON文件加载配置。
"""

import json
from pathlib import Path
from typing import Any


class ConfigManager:
    """配置管理器类.

    负责加载、验证和管理项目配置。
    """

    # TODO: 如果传入的是相对路径或文件名，则是相对于项目根目录的路径，而不是相对于当前文件的路径
    def __init__(self, config_file: str = ".espanso-llm-quick-translate.json") -> None:
        """初始化配置管理器.

        Args:
            config_file: 配置文件路径
        """
        self.config_file = Path(config_file)
        self._config: dict[str, Any] = {}
        self._load_config()

    def _load_config(self) -> None:
        """加载配置文件."""
        if not self.config_file.exists():
            msg = f"配置文件不存在: {self.config_file}"
            raise FileNotFoundError(msg)

        try:
            with Path.open(self.config_file, encoding="utf-8") as f:
                self._config = json.load(f)
        except json.JSONDecodeError as e:
            msg = f"配置文件格式错误: {e}"
            # TODO: Within an `except` clause, raise exceptions with `raise ... from err` or `raise ... from None` to distinguish them from errors in exception handling (RuffB904)
            raise ValueError(msg)

    # TODO: Dynamically typed expressions (typing.Any) are disallowed in `default` (RuffANN401)
    # TODO: Dynamically typed expressions (typing.Any) are disallowed in `get` (RuffANN401)
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值.

        Args:
            key: 配置键
            default: 默认值

        Returns
        -------
            配置值
        """
        return self._config.get(key, default)

    # TODO: Dynamically typed expressions (typing.Any) are disallowed in `get_required` (RuffANN401)
    def get_required(self, key: str) -> Any:
        """获取必需的配置值.

        Args:
            key: 配置键

        Returns
        -------
            配置值

        Raises
        ------
            ValueError: 如果配置值不存在
        """
        value = self._config.get(key)
        if value is None:
            msg = f"必需的配置项缺失: {key}"
            raise ValueError(msg)
        return value

    @property
    def api_key(self) -> str:
        """获取API密钥."""
        return self.get_required("api_key")

    @property
    def base_url(self) -> str:
        """获取基础URL."""
        return self.get_required("base_url")

    @property
    def model(self) -> str:
        """获取模型名称."""
        return self.get_required("model")

    @property
    def auto_play(self) -> bool:
        """获取是否自动播放."""
        return self.get("auto_play", "false").lower() == "true"

    @property
    # TODO: 如果传入的是相对路径或文件名，则是相对于项目根目录的路径，而不是相对于当前文件的路径
    def diff_output_path(self) -> str:
        """获取diff输出文件路径."""
        return self.get("diff_output_path", "diffs_text.txt")

    @property
    # TODO: 如果传入的是相对路径或文件名，则是相对于项目根目录的路径，而不是相对于当前文件的路径
    def audio_file_path(self) -> str:
        """获取音频文件路径."""
        return self.get("audio_file_path", "translated.mp3")

    @property
    # TODO: 如果传入的是相对路径或文件名，则是相对于项目根目录的路径，而不是相对于当前文件的路径
    def system_prompt_file(self) -> str:
        """获取系统提示文件路径."""
        return self.get("system_prompt_file", "src/resources/system_prompt.txt")

    @property
    def sound_name(self) -> str:
        """获取语音名称."""
        return self.get("sound_name", "en-GB-LibbyNeural")

    @property
    def target_language(self) -> str:
        """获取目标语言."""
        return self.get("target_language", "English")

    def validate(self) -> None:
        """验证配置完整性."""
        required_keys = ["api_key", "base_url", "model"]
        missing_keys = [key for key in required_keys if not self._config.get(key)]

        if missing_keys:
            msg = f"配置文件中缺少必需的配置项: {', '.join(missing_keys)}"
            raise ValueError(msg)
