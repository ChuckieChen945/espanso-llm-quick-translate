"""Diff服务模块.

处理diff文件的读写和管理。
"""

import os
import shutil
from pathlib import Path

from dotenv import load_dotenv

from config import ConfigManager
from utils.diff_utils import DiffUtils


class DiffService:
    """Diff服务类.

    处理diff文件的读写和管理。
    """

    def __init__(self, config: ConfigManager) -> None:
        """初始化Diff服务.

        Args:
            config: 配置管理器
        """
        self.config = config
        self.diff_file = Path(config.diff_output_path)

    def install_showdiffs_skin(self) -> None:
        """安装showdiffs皮肤."""
        if not Path(self.config.showdiffs_skin_path).exists():
            raw_skin_path = Path(__file__).parent.parent.parent / "resources" / "ShowDiffs.ini"
            # 复制皮肤文件到目标路径
            shutil.copy(raw_skin_path, self.config.showdiffs_skin_path)

    def write_diffs_to_file(
        self,
        new_original: str,
        new_translated: str,
        filepath: str | None = None,
    ) -> None:
        """将diff写入文件.

        Args:
            new_original: 新的原始文本
            new_translated: 新的翻译文本
            filepath: 文件路径，如果为None则使用配置中的路径
        """
        if filepath is None:
            filepath = self.diff_file

        # 加载旧的diff数据
        old_original, old_translated = self._load_old_diffs(filepath)

        # 转换颜色标签为透明版本
        a_original = DiffUtils.convert_to_transparent(old_original)
        a_translated = DiffUtils.convert_to_transparent(old_translated)

        # 写入新的diff数据
        with Path.open(filepath, "w", encoding="utf-8") as f:
            f.write(f"A_ORIGINAL={a_original}\n")
            f.write(f"A_TRANSLATED={a_translated}\n\n")
            f.write(f"B_ORIGINAL={new_original}\n")
            f.write(f"B_TRANSLATED={new_translated}")

    def _load_old_diffs(self, filepath: str) -> tuple[str, str]:
        """加载旧的diff数据.

        Args:
            filepath: 文件路径

        Returns
        -------
            原始文本和翻译文本的元组
        """
        if not Path(filepath).exists():
            return "", ""

        load_dotenv(filepath)
        old_original = os.getenv("B_ORIGINAL", "")
        old_translated = os.getenv("B_TRANSLATED", "")

        return old_original, old_translated

    def generate_and_write_diff(
        self,
        original_text: str,
        translated_text: str,
        filepath: str | None = None,
    ) -> None:
        """生成diff并写入文件.

        Args:
            original_text: 原始文本
            translated_text: 翻译文本
            filepath: 文件路径
        """
        # 生成diff
        original_aligned, translated_aligned = DiffUtils.generate_diff(
            original_text,
            translated_text,
        )

        # 写入文件
        self.write_diffs_to_file(original_aligned, translated_aligned, filepath)
        self.install_showdiffs_skin()

    def get_formatted_diff(self, original_text: str, translated_text: str) -> str:
        """获取格式化的差异文本.

        Args:
            original_text: 原始文本
            translated_text: 翻译文本

        Returns
        -------
            格式化的差异文本
        """
        return DiffUtils.format_diff_for_display(original_text, translated_text)
