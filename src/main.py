"""主程序模块.

espanso包的主入口点，处理翻译请求。支持详细的日志记录和错误处理。
优化为立即返回翻译结果，后台任务异步执行。
"""

import io
import sys
import time
from pathlib import Path

from core import ServiceFactory
from utils import setup_logging


def main() -> None:
    """主程序入口.

    解析参数，验证输入，调用翻译管理器，并立即打印结果给espanso。
    后台任务（音频生成、diff生成、自动播放）异步执行。
    """
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    start_time = time.time()

    # 设置日志记录
    log_file = Path(__file__).parent.parent / "logs" / "translation.log"
    logger = setup_logging(log_file=str(log_file))

    logger.info("=" * 50)
    logger.info("开始新的翻译请求")
    logger.info(f"命令行参数: {sys.argv}")

    if len(sys.argv) != 2:
        error_msg = '用法错误: python main.py "<text>"'
        logger.error(error_msg)
        # 使用 sys.stdout.write()，性能略高于print
        sys.stdout.write('❌ 用法错误: python main.py "<text>"')
        sys.stdout.flush()
        return

    original = sys.argv[1]
    if not original.strip():
        error_msg = "未提供要翻译的文本"
        logger.error(error_msg)
        # 使用 sys.stdout.write()，性能略高于print
        sys.stdout.write("❌ 错误: 未提供要翻译的文本!")
        sys.stdout.flush()
        return

    logger.info(f"输入文本长度: {len(original)}字符")
    logger.debug(f"输入文本: {original[:100]}{'...' if len(original) > 100 else ''}")

    try:
        # 使用服务工厂获取翻译管理器
        factory = ServiceFactory()
        translation_manager = factory.get_translation_manager()

        # 翻译文本（立即返回结果）
        translated = translation_manager.translate_text(original)

        total_time = time.time() - start_time
        logger.info(f"翻译请求完成，总耗时: {total_time:.2f}秒")
        logger.info(f"翻译结果: {translated[:100]}{'...' if len(translated) > 100 else ''}")

        # 立即输出翻译结果给espanso
        sys.stdout.write(translated)
        sys.stdout.flush()

        # 后台任务已在翻译管理器中异步启动，无需等待

    except FileNotFoundError as e:
        error_msg = f"配置文件错误: {e}"
        logger.error(error_msg, exc_info=True)
        sys.stdout.write(f"❌ 配置文件错误: {e}")
        sys.stdout.flush()
    except ValueError as e:
        error_msg = f"配置错误: {e}"
        logger.error(error_msg, exc_info=True)
        sys.stdout.write(f"❌ 配置错误: {e}")
        sys.stdout.flush()
    except Exception as e:
        total_time = time.time() - start_time
        error_msg = f"翻译失败: {e}"
        logger.error(f"{error_msg}，总耗时: {total_time:.2f}秒", exc_info=True)
        sys.stdout.write(f"❌ 翻译失败: {e}")
        sys.stdout.flush()

    finally:
        logger.info("翻译请求结束")
        logger.info("=" * 50)


if __name__ == "__main__":
    main()
