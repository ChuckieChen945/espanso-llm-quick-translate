"""Diff工具模块.

处理文本差异比较和格式化。
"""

import difflib
from enum import Enum


class DiffColor(Enum):
    """Diff颜色枚举."""

    GREEN = ("<green>", "</green>")  # 新增/相同
    RED = ("<red>", "</red>")  # 删除
    YELLOW = ("<yellow>", "</yellow>")  # 替换
    GREEN_TRANSPARENT = ("<green_t>", "</green_t>")  # 透明绿色
    RED_TRANSPARENT = ("<red_t>", "</red_t>")  # 透明红色
    YELLOW_TRANSPARENT = ("<yellow_t>", "</yellow_t>")  # 透明黄色


class DiffUtils:
    """Diff工具类.

    处理文本差异比较和格式化。
    """

    @staticmethod
    def convert_to_transparent(text: str) -> str:
        """将颜色标签转换为透明版本.

        Args:
            text: 原始文本

        Returns
        -------
            转换后的文本
        """
        if not text:
            return ""

        # 使用映射表进行转换
        color_mapping = {
            DiffColor.GREEN.value[0]: DiffColor.GREEN_TRANSPARENT.value[0],
            DiffColor.GREEN.value[1]: DiffColor.GREEN_TRANSPARENT.value[1],
            DiffColor.RED.value[0]: DiffColor.RED_TRANSPARENT.value[0],
            DiffColor.RED.value[1]: DiffColor.RED_TRANSPARENT.value[1],
            DiffColor.YELLOW.value[0]: DiffColor.YELLOW_TRANSPARENT.value[0],
            DiffColor.YELLOW.value[1]: DiffColor.YELLOW_TRANSPARENT.value[1],
        }

        for old_color, new_color in color_mapping.items():
            text = text.replace(old_color, new_color)

        return text

    @staticmethod
    def generate_diff(original: str, translated: str) -> tuple[str, str]:
        """生成文本差异.

        使用LCS（最长公共子序列）算法进行文本差异对齐。

        Args:
            original: 原始文本
            translated: 翻译文本

        Returns
        -------
            对齐后的原始文本和翻译文本
        """
        # 使用 difflib 进行文本比较
        matcher = difflib.SequenceMatcher(None, original, translated)
        original_aligned, translated_aligned = [], []

        for operation, i1, i2, j1, j2 in matcher.get_opcodes():
            original_segment = original[i1:i2]
            translated_segment = translated[j1:j2]

            if operation == "equal":
                # 相同部分：绿色
                original_aligned.append(
                    f"{DiffColor.GREEN.value[0]}{original_segment}{DiffColor.GREEN.value[1]}",
                )
                translated_aligned.append(
                    f"{DiffColor.GREEN.value[0]}{translated_segment}{DiffColor.GREEN.value[1]}",
                )
            elif operation == "delete":
                # 删除部分：红色
                original_aligned.append(
                    f"{DiffColor.RED.value[0]}{original_segment}{DiffColor.RED.value[1]}",
                )
                translated_aligned.append(
                    f"{DiffColor.RED.value[0]}{' ' * len(original_segment)}{DiffColor.RED.value[1]}",
                )
            elif operation == "insert":
                # 插入部分：红色
                original_aligned.append(
                    f"{DiffColor.RED.value[0]}{' ' * len(translated_segment)}{DiffColor.RED.value[1]}",
                )
                translated_aligned.append(
                    f"{DiffColor.RED.value[0]}{translated_segment}{DiffColor.RED.value[1]}",
                )
            elif operation == "replace":
                # 替换部分：黄色
                original_aligned.append(
                    f"{DiffColor.YELLOW.value[0]}{original_segment}{DiffColor.YELLOW.value[1]}",
                )
                translated_aligned.append(
                    f"{DiffColor.YELLOW.value[0]}{translated_segment}{DiffColor.YELLOW.value[1]}",
                )

        return "".join(original_aligned), "".join(translated_aligned)

    @staticmethod
    def format_diff_for_display(original: str, translated: str) -> str:
        """格式化差异用于显示.

        Args:
            original: 原始文本
            translated: 翻译文本

        Returns
        -------
            格式化的差异文本
        """
        original_diff, translated_diff = DiffUtils.generate_diff(original, translated)

        # 转换为透明版本用于显示
        original_transparent = DiffUtils.convert_to_transparent(original_diff)
        translated_transparent = DiffUtils.convert_to_transparent(translated_diff)

        return f"原文: {original_transparent}\n译文: {translated_transparent}"
