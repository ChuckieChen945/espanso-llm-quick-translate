"""音频生成脚本：独立进程生成TTS音频。"""

import sys
from pathlib import Path

from src.core import ServiceFactory
from src.utils import setup_logging


def main() -> None:
    """音频生成子进程入口."""
    if len(sys.argv) < 2:
        print("缺少参数：需要生成音频的文本", file=sys.stderr)
        sys.exit(1)
    text = sys.argv[1]
    log_file = Path(__file__).parent.parent.parent / "logs" / "audio_generate.log"
    logger = setup_logging(log_file=str(log_file))
    logger.info("= 音频生成子进程启动 =")
    try:
        factory = ServiceFactory()
        translation_manager = factory.get_translation_manager()
        # 直接同步生成音频
        import asyncio

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(translation_manager.audio_service.generate_tts_audio(text))
        loop.close()
        translation_manager.audio_service.play_last_audio()
        logger.info("音频生成完成")
    except Exception as e:
        logger.error(f"音频生成失败: {e}", exc_info=True)
        print(f"❌ 音频生成失败: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
