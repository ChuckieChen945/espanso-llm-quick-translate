"""Background worker.

这个文件的作用是，在 ask_ai.py 中被调用，用于生成 TTS 音频，并保存到文件中。
生成diff,按照规范保存到文件中

"""

import asyncio
import difflib
import os
import sys

from dotenv import load_dotenv
from edge_tts import Communicate
from playsound import playsound as _playsound


async def generate_tts_audio(
    text: str,
    filename: str = "translated.mp3",
    sound_name: str = "en-GB-LibbyNeural",
) -> None:
    """Generate TTS audio."""
    communicate = Communicate(text, sound_name)
    await communicate.save(filename)


### ✅ Diffing ###
def change_color(text: str) -> str:
    """_summary_.

    Args:
        text (str): _description_

    Returns
    -------
        str: _description_
    """
    if text:
        return (
            text.replace("<green>", "<green_t>")
            .replace("</green>", "</green_t>")
            .replace("<red>", "<red_t>")
            .replace("</red>", "</red_t>")
            .replace("<yellow>", "<yellow_t>")
            .replace("</yellow>", "</yellow_t>")
        )
    return None


def lcs_diff_align_desktop_info(a: str, b: str) -> tuple[str, str]:
    """_summary_.

    Args:
        a (str): _description_
        b (str): _description_

    Returns
    -------
        tuple[str, str]: _description_
    """
    sm = difflib.SequenceMatcher(None, a, b)
    a_aligned, b_aligned = [], []

    COLOR_GREEN = "<green>"  # 新增 - 柔和绿色
    COLOR_GREEN_STOP = "</green>"  # 新增 - 柔和绿色
    COLOR_RED = "<red>"  # 删除 - 柔和红色
    COLOR_RED_STOP = "</red>"  # 删除 - 柔和红色
    COLOR_YELLOW = "<yellow>"  # 替换 - 柔和黄色
    COLOR_YELLOW_STOP = "</yellow>"  # 替换 - 柔和黄色

    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        a_seg = a[i1:i2]
        b_seg = b[j1:j2]

        if tag == "equal":
            a_aligned.append(f"{COLOR_GREEN}{a_seg}{COLOR_GREEN_STOP}")
            b_aligned.append(f"{COLOR_GREEN}{b_seg}{COLOR_GREEN_STOP}")
        elif tag == "delete":
            a_aligned.append(f"{COLOR_RED}{a_seg}{COLOR_RED_STOP}")
            b_aligned.append(f"{COLOR_RED}{' ' * len(a_seg)}{COLOR_RED_STOP}")
        elif tag == "insert":
            a_aligned.append(f"{COLOR_RED}{' ' * len(b_seg)}{COLOR_RED_STOP}")
            b_aligned.append(f"{COLOR_RED}{b_seg}{COLOR_RED_STOP}")
        elif tag == "replace":
            a_aligned.append(f"{COLOR_YELLOW}{a_seg}{COLOR_YELLOW_STOP}")
            b_aligned.append(f"{COLOR_YELLOW}{b_seg}{COLOR_YELLOW_STOP}")

    return "".join(a_aligned), "".join(b_aligned)


def write_diffs_to_file(new_B_original: str, new_B_translated: str, filepath: str):
    load_dotenv(filepath)
    old_B_original = os.getenv("B_original")
    old_B_translated = os.getenv("B_translated")

    A_original = change_color(old_B_original)
    A_translated = change_color(old_B_translated)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"A_original={A_original}\n")
        f.write(f"A_translated={A_translated}\n" + "\n")
        f.write(f"B_original={new_B_original}\n")
        f.write(f"B_translated={new_B_translated}")


### ✅ Utility Modules ###
# TODO： 将其移到新文件中，以使 espanso 的 - trigger: "\x11" # <Ctrl-Q> 可以直接调用
def play_audio(filepath: str, block: bool = True):
    _playsound(filepath, block=block)


def background_worker(
    text: str,
    result: str,
    audio_file: str,
    diff_file: str,
    sound_name: str,
    auto_play: bool,
):
    original, translated = lcs_diff_align_desktop_info(text, result)
    write_diffs_to_file(original, translated, diff_file)
    asyncio.run(generate_tts_audio(result, audio_file, sound_name))
    if auto_play:
        play_audio(audio_file)


def main():
    if len(sys.argv) != 7:
        print(
            "❌ Usage: python background_worker.py <text> <result> <audio_file> <diff_file> <sound_name> <auto_play>",
        )
        sys.exit(1)

    text = sys.argv[1]
    result = sys.argv[2]
    audio_file = sys.argv[3]
    diff_file = sys.argv[4]
    sound_name = sys.argv[5]
    auto_play = sys.argv[6] == "true"

    try:
        background_worker(text, result, audio_file, diff_file, sound_name, auto_play)
    except Exception as e:
        print(f"❌ Background worker failed: {e}")


if __name__ == "__main__":
    main()
