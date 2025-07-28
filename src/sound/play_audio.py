"""音频播放模块.

package.yml 定义了 <Ctrl-Q> 快捷键，用于播放音频。

这个文件的作用是，在 package.yml 中被调用，用于播放音频。
"""

from src.core import ServiceFactory


def main() -> None:
    """主函数.

    播放最后生成的音频文件。
    """
    try:
        # 使用服务工厂获取翻译管理器
        factory = ServiceFactory()
        translation_manager = factory.get_translation_manager()

        # 播放最后生成的音频
        translation_manager.play_last_audio()
        # 只播放音频，输出空内容给espanso
        print()

    except FileNotFoundError as e:
        print(f"❌ 配置文件错误: {e}")
    except ValueError as e:
        print(f"❌ 配置错误: {e}")
    except Exception as e:
        print(f"❌ 音频播放失败: {e}")


if __name__ == "__main__":
    main()
