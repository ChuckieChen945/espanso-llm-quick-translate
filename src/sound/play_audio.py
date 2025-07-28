"""音频播放模块.

package.yml 定义了 <Ctrl-Q> 快捷键，用于播放音频。

这个文件的作用是，在 package.yml 中被调用，用于播放音频。
"""

from pathlib import Path

from src.core import ServiceFactory
from src.utils import setup_logging


def main() -> None:
    """主函数.

    播放最后生成的音频文件。
    """
    # 设置日志记录
    log_file = Path(__file__).parent.parent.parent / "logs" / "audio.log"
    logger = setup_logging(log_file=str(log_file))

    try:
        logger.info("开始播放音频")

        # 使用服务工厂获取翻译管理器
        factory = ServiceFactory()
        translation_manager = factory.get_translation_manager()

        # 播放最后生成的音频
        translation_manager.play_last_audio()
        logger.info("音频播放完成")

        # 只播放音频，输出空内容给espanso
        print()

    except FileNotFoundError as e:
        logger.error(f"配置文件错误: {e}")
        print(f"❌ 配置文件错误: {e}")
    except ValueError as e:
        logger.error(f"配置错误: {e}")
        print(f"❌ 配置错误: {e}")
    except Exception as e:
        logger.error(f"音频播放失败: {e}", exc_info=True)
        print(f"❌ 音频播放失败: {e}")


if __name__ == "__main__":
    main()
