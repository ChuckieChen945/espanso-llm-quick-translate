"""主程序模块.

espanso包的主入口点，处理翻译请求。
"""

import sys
from pathlib import Path

from core import ServiceFactory
from utils import setup_logging


def main() -> None:
    """主程序入口.

    解析参数，验证输入，调用翻译管理器，并打印结果。
    """
    # 设置日志记录
    log_file = Path(__file__).parent.parent / "logs" / "translation.log"
    logger = setup_logging(log_file=str(log_file))

    if len(sys.argv) != 2:
        logger.error('用法错误: python main.py "<text>"')
        print('❌ 用法错误: python main.py "<text>"')
        return

    original = sys.argv[1]
    if not original.strip():
        logger.error("未提供要翻译的文本")
        print("❌ 错误: 未提供要翻译的文本!")
        return

    try:
        logger.info(f"开始翻译文本: {original[:50]}{'...' if len(original) > 50 else ''}")

        # 使用服务工厂获取翻译管理器
        factory = ServiceFactory()
        translation_manager = factory.get_translation_manager()

        # 翻译文本
        translated = translation_manager.translate_text(original)
        logger.info(f"翻译完成: {translated[:50]}{'...' if len(translated) > 50 else ''}")

        print(translated, flush=True)

    except FileNotFoundError as e:
        logger.error(f"配置文件错误: {e}")
        print(f"❌ 配置文件错误: {e}")
    except ValueError as e:
        logger.error(f"配置错误: {e}")
        print(f"❌ 配置错误: {e}")
    except Exception as e:
        logger.error(f"翻译失败: {e}", exc_info=True)
        print(f"❌ 翻译失败: {e}")


if __name__ == "__main__":
    main()
