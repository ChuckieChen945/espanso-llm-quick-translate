"""配置管理模块.

统一管理项目配置，支持从JSON文件加载配置。
支持代理配置和其他高级选项。
"""

import json
from pathlib import Path
from typing import Any


class ConfigManager:
    """配置管理器类.

    负责加载、验证和管理项目配置。支持代理配置和其他高级选项。
    """

    def __init__(self, config_file: str = ".espanso-llm-quick-translate.json") -> None:
        """初始化配置管理器.

        Args:
            config_file: 配置文件路径，支持相对路径和绝对路径
        """
        # 处理相对路径，相对于项目根目录
        if not Path(config_file).is_absolute():
            # 获取项目根目录（src的父目录）
            project_root = Path(__file__).parent.parent.parent
            self.config_file = project_root / config_file
        else:
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
            raise ValueError(msg) from e

    def get(self, key: str, default: str | None = None) -> str:
        """获取配置值.

        Args:
            key: 配置键
            default: 默认值

        Returns
        -------
            配置值
        """
        return self._config.get(key, default)

    def get_required(self, key: str) -> str:
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
        return str(value)

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
    def proxy(self) -> str | None:
        """获取代理URL."""
        return self.get("proxy")

    @property
    def auto_play(self) -> bool:
        """获取是否自动播放."""
        return self.get("auto_play", "false").lower() == "true"

    @property
    def diff_output_path(self) -> str:
        """获取diff输出文件路径."""
        path = self.get("diff_output_path", "diffs_text.txt")
        # 处理相对路径
        if not Path(path).is_absolute():
            project_root = Path(__file__).parent.parent.parent
            return str(project_root / path)
        return path

    @property
    def audio_file_path(self) -> str:
        """获取音频文件路径."""
        path = self.get("audio_file_path", "translated.mp3")
        # 处理相对路径
        if not Path(path).is_absolute():
            project_root = Path(__file__).parent.parent.parent
            return str(project_root / path)
        return path

    @property
    def system_prompt_file(self) -> str:
        """获取系统提示文件路径."""
        path = self.get("system_prompt_file", "src/resources/system_prompt.txt")
        # 处理相对路径
        if not Path(path).is_absolute():
            project_root = Path(__file__).parent.parent.parent
            return str(project_root / path)
        return path

    @property
    def showdiffs_skin_path(self) -> str:
        """获取showdiffs皮肤文件路径."""
        path = self.get(
            "showdiffs_skin_path",
        )
        # 处理相对路径
        if not Path(path).is_absolute():
            project_root = Path(__file__).parent.parent.parent
            return str(project_root / path)
        return path

    @property
    def sound_name(self) -> str:
        """获取语音名称."""
        return self.get("sound_name", "en-GB-LibbyNeural")

    @property
    def target_language(self) -> str:
        """获取目标语言."""
        return self.get("target_language", "English")

    @property
    def timeout(self) -> int:
        """获取超时时间（秒）."""
        return int(self.get("timeout", "30"))

    @property
    def max_retries(self) -> int:
        """获取最大重试次数."""
        return int(self.get("max_retries", "3"))

    @property
    def log_level(self) -> str:
        """获取日志级别."""
        return self.get("log_level", "INFO")

    def validate(self) -> None:
        """验证配置完整性."""
        required_keys = ["api_key", "base_url", "model"]
        missing_keys = [key for key in required_keys if not self._config.get(key)]

        if missing_keys:
            msg = f"配置文件中缺少必需的配置项: {', '.join(missing_keys)}"
            raise ValueError(msg)

    def get_all_config(self) -> dict[str, Any]:
        """获取所有配置（用于调试）.

        Returns
        -------
            所有配置的字典
        """
        return {
            "api_key": self.api_key,
            "base_url": self.base_url,
            "model": self.model,
            "proxy": self.proxy,
            "auto_play": self.auto_play,
            "diff_output_path": self.diff_output_path,
            "audio_file_path": self.audio_file_path,
            "system_prompt_file": self.system_prompt_file,
            "showdiffs_skin_path": self.showdiffs_skin_path,
            "sound_name": self.sound_name,
            "target_language": self.target_language,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "log_level": self.log_level,
        }
