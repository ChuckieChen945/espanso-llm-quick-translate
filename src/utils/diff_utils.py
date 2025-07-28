"""Diff工具模块.

处理文本差异比较和格式化。
"""

import difflib


class DiffUtils:
    """Diff工具类.

    处理文本差异比较和格式化。
    """

    # 颜色标签常量
    COLOR_GREEN = "<green>"  # 新增 - 柔和绿色
    COLOR_GREEN_STOP = "</green>"
    COLOR_RED = "<red>"  # 删除 - 柔和红色
    COLOR_RED_STOP = "</red>"
    COLOR_YELLOW = "<yellow>"  # 替换 - 柔和黄色
    COLOR_YELLOW_STOP = "</yellow>"

    @staticmethod
    def change_color_transparent(text: str) -> str:
        """转换颜色标签.

        Args:
            text: 原始文本

        Returns
        -------
            转换后的文本
        """
        if not text:
            return ""

        return (
            text.replace("<green>", "<green_t>")
            .replace("</green>", "</green_t>")
            .replace("<red>", "<red_t>")
            .replace("</red>", "</red_t>")
            .replace("<yellow>", "<yellow_t>")
            .replace("</yellow>", "</yellow_t>")
        )

    @staticmethod
    def lcs_diff_align_desktop_info(a: str, b: str) -> tuple[str, str]:
        """使用LCS算法进行文本差异对齐.

        Args:
            a: 原始文本
            b: 新文本

        Returns
        -------
            对齐后的原始文本和新文本
        """
        sm = difflib.SequenceMatcher(None, a, b)
        a_aligned, b_aligned = [], []

        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            a_seg = a[i1:i2]
            b_seg = b[j1:j2]

            if tag == "equal":
                a_aligned.append(f"{DiffUtils.COLOR_GREEN}{a_seg}{DiffUtils.COLOR_GREEN_STOP}")
                b_aligned.append(f"{DiffUtils.COLOR_GREEN}{b_seg}{DiffUtils.COLOR_GREEN_STOP}")
            elif tag == "delete":
                a_aligned.append(f"{DiffUtils.COLOR_RED}{a_seg}{DiffUtils.COLOR_RED_STOP}")
                b_aligned.append(
                    f"{DiffUtils.COLOR_RED}{' ' * len(a_seg)}{DiffUtils.COLOR_RED_STOP}",
                )
            elif tag == "insert":
                a_aligned.append(
                    f"{DiffUtils.COLOR_RED}{' ' * len(b_seg)}{DiffUtils.COLOR_RED_STOP}",
                )
                b_aligned.append(f"{DiffUtils.COLOR_RED}{b_seg}{DiffUtils.COLOR_RED_STOP}")
            elif tag == "replace":
                a_aligned.append(f"{DiffUtils.COLOR_YELLOW}{a_seg}{DiffUtils.COLOR_YELLOW_STOP}")
                b_aligned.append(f"{DiffUtils.COLOR_YELLOW}{b_seg}{DiffUtils.COLOR_YELLOW_STOP}")

        return "".join(a_aligned), "".join(b_aligned)
