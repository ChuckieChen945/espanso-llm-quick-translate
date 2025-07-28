"""音频播放模块.

package.yml 定义了 <Ctrl-Q> 快捷键，用于播放音频。
优化为支持详细的日志记录和错误处理，立即返回结果给espanso。
"""

import io
import sys
import time
from pathlib import Path

from playsound import playsound
from src.config import ConfigManager
from src.utils import setup_logging


def main() -> None:
    """主函数.

    播放最后生成的音频文件。立即返回结果给espanso，然后异步播放音频。
    """
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    start_time = time.time()

    # 设置日志记录
    log_file = Path(__file__).parent.parent.parent / "logs" / "audio.log"
    logger = setup_logging(log_file=str(log_file))

    logger.info("=" * 50)
    logger.info("开始音频播放请求")

    try:
        config = ConfigManager()
        # 检查是否有可播放的音频文件
        if config.audio_file_path is None:
            error_msg = "没有可播放的音频文件"
            logger.warning(error_msg)
            # 立即返回错误信息给espanso
            sys.stdout.write("❌ 没有可播放的音频文件")
            sys.stdout.flush()
            return

        logger.info(f"播放音频文件: {config.audio_file_path}")

        # 立即返回空内容给espanso，然后异步播放音频
        sys.stdout.write("")
        sys.stdout.flush()

        # 在后台异步播放音频
        import threading

        audio_thread = threading.Thread(
            target=playsound(config.audio_file_path, block=True),
            daemon=True,
        )
        audio_thread.start()

        total_time = time.time() - start_time
        logger.info(f"音频播放请求完成，总耗时: {total_time:.2f}秒")

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
