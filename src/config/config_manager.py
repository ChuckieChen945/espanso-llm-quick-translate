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

    def validate(self) -> None:
        """验证配置完整性."""
        required_keys = ["api_key", "base_url", "model"]
        missing_keys = [key for key in required_keys if not self._config.get(key)]

        if missing_keys:
            msg = f"配置文件中缺少必需的配置项: {', '.join(missing_keys)}"
            raise ValueError(msg)
