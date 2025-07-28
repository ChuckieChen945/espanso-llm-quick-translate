"""主程序模块.

espanso包的主入口点，处理翻译请求。
"""

import sys

from core import ServiceFactory


def main() -> None:
    """主程序入口.

    解析参数，验证输入，调用翻译管理器，并打印结果。
    """
    if len(sys.argv) != 2:
        print('❌ 用法错误: python main.py "<text>"')
        return

    original = sys.argv[1]
    if not original.strip():
        print("❌ 错误: 未提供要翻译的文本!")
        return

    try:
        # 使用服务工厂获取翻译管理器
        factory = ServiceFactory()
        translation_manager = factory.get_translation_manager()

        # 翻译文本
        translated = translation_manager.translate_text(original)
        print(translated, flush=True)

    except FileNotFoundError as e:
        print(f"❌ 配置文件错误: {e}")
    except ValueError as e:
        print(f"❌ 配置错误: {e}")
    except Exception as e:
        print(f"❌ 翻译失败: {e}")


if __name__ == "__main__":
    main()
