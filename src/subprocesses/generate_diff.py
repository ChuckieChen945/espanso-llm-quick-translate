"""diff生成脚本：独立进程生成diff并写入文件。"""

import sys
from pathlib import Path

from src.config import ConfigManager
from src.services import DiffService
from src.utils import setup_logging


def main() -> None:
    """diff生成子进程入口."""
    if len(sys.argv) < 3:
        print("缺少参数：需要原文和译文", file=sys.stderr)
        sys.exit(1)
    original = sys.argv[1]
    translated = sys.argv[2]
    log_file = Path(__file__).parent.parent.parent / "logs" / "diff_generate.log"
    logger = setup_logging(log_file=str(log_file))
    logger.info("= diff生成子进程启动 =")
    try:
        config = ConfigManager()
        diff_service = DiffService(config)
        diff_service.generate_and_write_diff(original, translated)
        logger.info("diff生成完成")
    except Exception as e:
        logger.error(f"diff生成失败: {e}", exc_info=True)
        print(f"❌ diff生成失败: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
