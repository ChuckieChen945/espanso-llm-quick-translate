"""集成测试模块.

测试重构后的翻译功能，包括后台异步任务。
"""

import asyncio
import time
from pathlib import Path

from src.config import ConfigManager
from src.core import ServiceFactory


def test_translation_flow():
    """测试翻译流程."""
    print("=" * 50)
    print("开始集成测试")
    print("=" * 50)

    try:
        # 初始化配置和服务
        config = ConfigManager()
        factory = ServiceFactory()
        translation_manager = factory.get_translation_manager()

        print("✅ 配置和服务初始化成功")

        # 测试翻译
        test_text = "Hello world, this is a test."
        print(f"📝 测试文本: {test_text}")

        start_time = time.time()
        translated = translation_manager.translate_text(test_text)
        translation_time = time.time() - start_time

        print(f"✅ 翻译完成，耗时: {translation_time:.2f}秒")
        print(f"📄 翻译结果: {translated}")

        # 等待后台任务完成
        print("⏳ 等待后台任务完成...")
        translation_manager.wait_for_background_tasks()
        print("✅ 后台任务完成")

        # 检查音频文件
        if translation_manager.last_audio_file:
            audio_path = Path(translation_manager.last_audio_file)
            if audio_path.exists():
                print(f"✅ 音频文件生成成功: {audio_path}")
                print(f"📊 文件大小: {audio_path.stat().st_size / 1024:.1f}KB")
            else:
                print("❌ 音频文件不存在")
        else:
            print("⚠️ 没有音频文件路径")

        # 检查diff文件
        diff_path = Path(config.diff_output_path)
        if diff_path.exists():
            print(f"✅ Diff文件生成成功: {diff_path}")
            print(f"📊 文件大小: {diff_path.stat().st_size / 1024:.1f}KB")
        else:
            print("❌ Diff文件不存在")

        print("=" * 50)
        print("集成测试完成")
        print("=" * 50)

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback

        traceback.print_exc()


def test_audio_playback():
    """测试音频播放功能."""
    print("=" * 30)
    print("测试音频播放功能")
    print("=" * 30)

    try:
        config = ConfigManager()
        factory = ServiceFactory()
        translation_manager = factory.get_translation_manager()

        if translation_manager.last_audio_file:
            print(f"🎵 播放音频: {translation_manager.last_audio_file}")
            translation_manager.play_last_audio()
            print("✅ 音频播放完成")
        else:
            print("❌ 没有可播放的音频文件")

    except Exception as e:
        print(f"❌ 音频播放测试失败: {e}")


def test_config_validation():
    """测试配置验证."""
    print("=" * 30)
    print("测试配置验证")
    print("=" * 30)

    try:
        config = ConfigManager()
        config.validate()
        print("✅ 配置验证通过")

        # 显示所有配置
        all_config = config.get_all_config()
        print("📋 当前配置:")
        for key, value in all_config.items():
            if key == "api_key":
                print(f"  {key}: {'*' * 10}")
            else:
                print(f"  {key}: {value}")

    except Exception as e:
        print(f"❌ 配置验证失败: {e}")


if __name__ == "__main__":
    print("🚀 开始运行集成测试")

    # 测试配置验证
    test_config_validation()
    print()

    # 测试翻译流程
    test_translation_flow()
    print()

    # 测试音频播放
    test_audio_playback()

    print("🎉 所有测试完成")
