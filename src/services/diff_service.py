"""Diff服务模块.

处理diff文件的读写和管理。支持详细的日志记录和错误处理。
"""

import os
import shutil
import time
from pathlib import Path

from dotenv import load_dotenv
from src.config import ConfigManager
from src.utils import get_logger
from src.utils.diff_utils import DiffUtils


class DiffService:
    """Diff服务类.

    处理diff文件的读写和管理。支持详细的日志记录和错误处理。
    """

    def __init__(self, config: ConfigManager) -> None:
        """初始化Diff服务.

        Args:
            config: 配置管理器
        """
        self.config = config
        self.diff_file = Path(config.diff_output_path)
        self.logger = get_logger("DiffService")

    def install_showdiffs_skin(self) -> None:
        """安装showdiffs皮肤."""
        try:
            if not Path(self.config.showdiffs_skin_path).exists():
                raw_skin_path = Path(__file__).parent.parent.parent / "resources" / "ShowDiffs.ini"

                if not raw_skin_path.exists():
                    self.logger.warning(f"原始皮肤文件不存在: {raw_skin_path}")
                    return

                # 确保目标目录存在
                target_path = Path(self.config.showdiffs_skin_path)
                target_path.parent.mkdir(parents=True, exist_ok=True)

                # 复制皮肤文件到目标路径
                shutil.copy(raw_skin_path, self.config.showdiffs_skin_path)
                self.logger.info(f"成功安装showdiffs皮肤: {self.config.showdiffs_skin_path}")
            else:
                self.logger.debug("showdiffs皮肤已存在，跳过安装")

        except Exception as e:
            self.logger.error(f"安装showdiffs皮肤失败: {e}", exc_info=True)

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

        Raises
        ------
            Exception: 写入过程中的任何错误
        """
        start_time = time.time()

        if filepath is None:
            filepath = self.diff_file

        self.logger.info(f"开始写入diff文件: {filepath}")
        self.logger.debug(f"原始文本长度: {len(new_original)}字符")
        self.logger.debug(f"翻译文本长度: {len(new_translated)}字符")

        try:
            # 确保输出目录存在
            output_path = Path(filepath)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # 加载旧的diff数据
            old_original, old_translated = self._load_old_diffs(filepath)

            # 转换颜色标签为透明版本
            a_original = DiffUtils.convert_to_transparent(old_original)
            a_translated = DiffUtils.convert_to_transparent(old_translated)

            # 写入新的diff数据
            with Path.open(filepath, "w", encoding="gb2312") as f:
                f.write(f"A_ORIGINAL={a_original}\n")
                f.write(f"A_TRANSLATED={a_translated}\n\n")
                f.write(f"B_ORIGINAL={new_original}\n")
                f.write(f"B_TRANSLATED={new_translated}")

            write_time = time.time() - start_time
            file_size = Path(filepath).stat().st_size / 1024  # KB
            self.logger.info(
                f"diff文件写入成功，耗时: {write_time:.2f}秒，文件大小: {file_size:.1f}KB",
            )

        except Exception as e:
            write_time = time.time() - start_time
            self.logger.error(
                f"diff文件写入失败，耗时: {write_time:.2f}秒，错误: {e}",
                exc_info=True,
            )
            msg = f"diff文件写入失败: {e}"
            raise Exception(msg) from e

    def _load_old_diffs(self, filepath: str) -> tuple[str, str]:
        """加载旧的diff数据.

        Args:
            filepath: 文件路径

        Returns
        -------
            原始文本和翻译文本的元组
        """
        if not Path(filepath).exists():
            self.logger.debug("diff文件不存在，使用空数据")
            return "", ""

        try:
            load_dotenv(filepath, encoding="gb2312")
            old_original = os.getenv("B_ORIGINAL", "")
            old_translated = os.getenv("B_TRANSLATED", "")

            self.logger.debug(f"成功加载旧diff数据，原始文本长度: {len(old_original)}字符")
        except Exception as e:
            self.logger.warning(f"加载旧diff数据失败: {e}")
            return "", ""
        else:
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

        Raises
        ------
            Exception: diff生成或写入过程中的任何错误
        """
        start_time = time.time()
        self.logger.info("开始生成diff")

        try:
            # 生成diff
            original_aligned, translated_aligned = DiffUtils.generate_diff(
                original_text,
                translated_text,
            )

            diff_time = time.time() - start_time
            self.logger.info(f"diff生成完成，耗时: {diff_time:.2f}秒")

            # 写入文件
            self.write_diffs_to_file(original_aligned, translated_aligned, filepath)

            # 安装皮肤
            self.install_showdiffs_skin()

            total_time = time.time() - start_time
            self.logger.info(f"diff处理完成，总耗时: {total_time:.2f}秒")

        except Exception as e:
            total_time = time.time() - start_time
            self.logger.error(f"diff处理失败，总耗时: {total_time:.2f}秒，错误: {e}", exc_info=True)
            msg = f"diff处理失败: {e}"
            raise Exception(msg) from e

    def get_formatted_diff(self, original_text: str, translated_text: str) -> str:
        """获取格式化的差异文本.

        Args:
            original_text: 原始文本
            translated_text: 翻译文本

        Returns
        -------
            格式化的差异文本
        """
        try:
            self.logger.debug("开始格式化diff显示")
            formatted_diff = DiffUtils.format_diff_for_display(original_text, translated_text)
            self.logger.debug("diff格式化完成")

        except Exception as e:
            self.logger.error(f"diff格式化失败: {e}", exc_info=True)
            return f"原文: {original_text}\n译文: {translated_text}"
        else:
            return formatted_diff
