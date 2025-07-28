"""音频播放模块.

package.yml 定义了 <Ctrl-Q> 快捷键，用于播放音频。
优化为支持详细的日志记录和错误处理。
"""

import io
import sys
import time
from pathlib import Path

from src.core import ServiceFactory
from src.utils import setup_logging


def main() -> None:
    """主函数.

    播放最后生成的音频文件。优化为支持详细的日志记录和错误处理。
    """
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    start_time = time.time()

    # 设置日志记录
    log_file = Path(__file__).parent.parent.parent / "logs" / "audio.log"
    logger = setup_logging(log_file=str(log_file))

    logger.info("=" * 50)
    logger.info("开始音频播放请求")

    try:
        # 使用服务工厂获取翻译管理器
        factory = ServiceFactory()
        translation_manager = factory.get_translation_manager()

        # 检查是否有可播放的音频文件
        if translation_manager.last_audio_file is None:
            error_msg = "没有可播放的音频文件"
            logger.warning(error_msg)
            sys.stdout.write("❌ 没有可播放的音频文件")
            sys.stdout.flush()
            return

        logger.info(f"播放音频文件: {translation_manager.last_audio_file}")

        # 播放最后生成的音频
        translation_manager.play_last_audio()

        total_time = time.time() - start_time
        logger.info(f"音频播放完成，总耗时: {total_time:.2f}秒")

        # 只播放音频，输出空内容给espanso
        # TODO: 开始进程后先立即输出 空内容 给 espanso，然后异步执行播放音频
        sys.stdout.write("")
        sys.stdout.flush()

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
        error_msg = f"音频播放失败: {e}"
        logger.error(f"{error_msg}，总耗时: {total_time:.2f}秒", exc_info=True)
        sys.stdout.write(f"❌ 音频播放失败: {e}")
        sys.stdout.flush()

    finally:
        logger.info("音频播放请求结束")
        logger.info("=" * 50)


if __name__ == "__main__":
    main()
