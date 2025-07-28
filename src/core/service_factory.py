"""服务工厂模块.

管理服务实例的创建和生命周期。
"""

from typing import Optional

from src.config import ConfigManager
from src.core.translation_manager import TranslationManager


class ServiceFactory:
    """服务工厂类.

    管理服务实例的创建和生命周期。
    """

    _instance: Optional["ServiceFactory"] = None
    _config: ConfigManager | None = None
    _translation_manager: TranslationManager | None = None

    def __new__(cls) -> "ServiceFactory":
        """单例模式实现."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """初始化服务工厂."""
        # 单例模式，避免重复初始化
        if hasattr(self, "_initialized"):
            return

        self._initialized = True

    def get_config(self, config_file: str = ".espanso-llm-quick-translate.json") -> ConfigManager:
        """获取配置管理器实例.

        Args:
            config_file: 配置文件路径

        Returns
        -------
            配置管理器实例
        """
        if self._config is None:
            self._config = ConfigManager(config_file)
            self._config.validate()

        return self._config

    def get_translation_manager(self, config: ConfigManager | None = None) -> TranslationManager:
        """获取翻译管理器实例.

        Args:
            config: 配置管理器，如果为None则使用默认配置

        Returns
        -------
            翻译管理器实例
        """
        if config is None:
            config = self.get_config()

        if self._translation_manager is None:
            self._translation_manager = TranslationManager(config)

        return self._translation_manager

    def reset(self) -> None:
        """重置所有服务实例."""
        self._config = None
        self._translation_manager = None
