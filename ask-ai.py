#!/usr/bin/env python

"""
ask-ai.py: Query a local or remote LLM (Large Language Model) using the OpenAI API interface and return the response.

Author: Bernhard Enders
Date: 2025-06-14
Version: 0.1.0

Description:
    This script is designed for integration with Espanso, allowing users to send a prompt to an LLM and receive a direct answer, suitable for text expansion workflows.

Features:
    - Loads configuration (API key, base URL, model) from a .env file in the script directory.
    - Sends the user-provided prompt to the LLM with a system message enforcing non-interactive, assumption-based responses.
    - Prints the LLM's response to stdout for Espanso to capture.
    - Handles errors gracefully and provides clear error messages if configuration or API calls fail.

Usage:
    python ask-ai.py "<text>"

Requirements:
    - openai
    - python-dotenv
    - Python 3.9+
"""

import os
import sys

parent_folder_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(parent_folder_path)
sys.path.append(os.path.join(parent_folder_path, "lib"))

import shutil
import difflib
import asyncio
from edge_tts import Communicate
from playsound import playsound
sys.stdout.reconfigure(encoding="utf-8")

# packages dependency check
REQUIRED_PACKAGES = ["openai", "dotenv"]
missing = []
for pkg in REQUIRED_PACKAGES:
    try:
        __import__(pkg)
    except ImportError:
        missing.append(pkg)
if missing:
    print(f"❌ Error: Missing required packages: {', '.join(missing)}. Please install them with 'pip install -r requirements.txt'.")
    sys.exit(0)

from openai import OpenAI
from dotenv import load_dotenv

async def generate_tts_audio(text: str, filename: str = "output.mp3"):
    communicate = Communicate(text, "en-GB-LibbyNeural")
    await communicate.save(filename)

def change_color(s:str):
    # TODO：右对齐
    s = s.replace('<green>','<green_t>')
    s = s.replace('</green>','</green_t>')
    s = s.replace('<red>','<red_t>')
    s = s.replace('</red>','</red_t>')
    s = s.replace('<yellow>','<yellow_t>')
    s = s.replace('</yellow>','</yellow_t>')
    return s

def write_diffs(new_B1:str,new_B2:str):

    dotenv_path = os.path.join(os.path.dirname(__file__), "diffs_text.txt")
    load_dotenv(dotenv_path)
    A1 = os.getenv("A1")
    A2 = os.getenv("A2")
    B1 = os.getenv("B1")
    B2 = os.getenv("B2")

    A1 = change_color(B1)
    A2 = change_color(B2)
    B1 = new_B1
    B2 = new_B2

    with open(dotenv_path, "w", encoding="utf-8") as f:
        f.write(f"A1={A1}\n")
        f.write(f"A2={A2}\n" + "\n")
        f.write(f"B1={B1}\n")
        f.write(f"B2={B2}")


def lcs_diff_align_desktop_info(a: str, b: str):
    sm = difflib.SequenceMatcher(None, a, b)

    a_aligned = []
    b_aligned = []

    COLOR_GREEN = '<green>'   # 新增 - 柔和绿色
    COLOR_GREEN_STOP = '</green>'   # 新增 - 柔和绿色
    COLOR_RED = '<red>'     # 删除 - 柔和红色
    COLOR_RED_STOP = '</red>'     # 删除 - 柔和红色
    COLOR_YELLOW = '<yellow>'  # 替换 - 柔和黄色
    COLOR_YELLOW_STOP = '</yellow>'  # 替换 - 柔和黄色

    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        a_seg = a[i1:i2]
        b_seg = b[j1:j2]

        if tag == 'equal':
            a_aligned.append(f"{COLOR_GREEN}{a_seg}{COLOR_GREEN_STOP}")
            b_aligned.append(f"{COLOR_GREEN}{b_seg}{COLOR_GREEN_STOP}")
        elif tag == 'delete':
            a_aligned.append(f"{COLOR_RED}{a_seg}{COLOR_RED_STOP}")
            b_aligned.append(f"{COLOR_RED}{' ' * len(a_seg)}{COLOR_RED_STOP}")
        elif tag == 'insert':
            a_aligned.append(f"{COLOR_RED}{' ' * len(b_seg)}{COLOR_RED_STOP}")
            b_aligned.append(f"{COLOR_RED}{b_seg}{COLOR_RED_STOP}")
        elif tag == 'replace':
            a_aligned.append(f"{COLOR_YELLOW}{a_seg}{COLOR_YELLOW_STOP}")
            b_aligned.append(f"{COLOR_YELLOW}{b_seg}{COLOR_YELLOW_STOP}")

    return ''.join(a_aligned), ''.join(b_aligned)

def ensure_env_file() -> None:
    """
    Ensures that a .env file exists. If not, tries to copy example.env to .env using shutil.copy.
    Raises FileNotFoundError if neither exists, lets OSError propagate on copy failure.
    """
    script_dir = os.path.dirname(__file__)
    env_path = os.path.join(script_dir, ".env")
    example_env_path = os.path.join(script_dir, "example.env")

    if not os.path.exists(env_path):
        if os.path.exists(example_env_path):
            shutil.copy(example_env_path, env_path)
        else:
            raise FileNotFoundError(f"❌ Error: Missing .env file in directory: '{script_dir}'.")

def load_and_validate_env() -> tuple[str, str, str]:
    """
    Loads and validates .env configuration. Returns (api_key, base_url, model).
    Raises ValueError if any required variable is missing.
    """
    dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
    load_dotenv(dotenv_path)
    api_key = os.getenv("API_KEY")
    base_url = os.getenv("BASE_URL")
    model = os.getenv("MODEL")
    if not api_key:
        raise ValueError("❌ Error: API_KEY variable not found in .env file!")
    if not base_url:
        raise ValueError("❌ Error: BASE_URL variable not found in .env file!")
    if not model:
        raise ValueError("❌ Error: MODEL variable not found in .env file!")
    return api_key, base_url, model

def ask_ai(text: str) -> str:
    """
    Sends a prompt to a local or remote LLM using the OpenAI API interface and returns the response.

    Args:
        text (str): The user prompt to send to the LLM.

    Returns:
        str: The LLM's response or an error message.
    """
    try:
        ensure_env_file()
        api_key, base_url, model = load_and_validate_env()
        client = OpenAI(api_key=api_key, base_url=base_url)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a 'translation expert'. Translate everything the user sends you into natural, idiomatic English, no matter what it is. If the user's input is already acceptable English, keep it unchanged. Respond with the translated English only.\n"
                        "Purpose and Goals:\n"
                        "* Provide accurate and contextually appropriate translations from any language into natural, idiomatic English.\n"
                        "* Identify when user input is already acceptable English and leave it unchanged.\n"
                        "* Offer translations that sound native and fluid, avoiding literal or awkward phrasing.\n"
                        "Behaviors and Rules:\n"
                        "1) Translation Process:\n"
                        "   a) Analyze the user's input to determine the source language and the intended meaning.\n"
                        "   b) Focus on conveying the nuance and idiom of the original text in English, rather than a word-for-word translation.\n"
                        "   c) If there are multiple valid translations for a phrase, choose the one that best fits the likely context.\n"
                        "   d) Do not add any conversational filler or extra information; respond with the translated English only.\n"
                        "   e) If the input is already in natural, idiomatic English, simply repeat the input as your response.\n"
                        "2) Handling Ambiguity/Idioms:\n"
                        "   a) If the source text contains idioms or cultural references, translate them into their English equivalents if possible, or provide a natural English rephrasing that captures the meaning.\n"
                        "   b) If a phrase is genuinely ambiguous without further context, provide the most common or likely translation.\n"
                        "Overall Tone:\n"
                        "* Be precise and authoritative in your translations.\n"
                        "* Maintain a professional and efficient demeanor.\n"
                        "* Focus solely on the task of translation, without extraneous conversation.\n"
                    ),
                },
                {
                    "role": "user",
                    "content": text,
                },
            ],
            stream=False,
        )
        answer = response.choices[0].message.content.strip()
        return answer
    except Exception:
        return "❌ Error: An unexpected error occurred while processing your request. Check model name, api key etc... and try again later."

def main() -> None:
    """
    Main entry point for the script. Parses arguments, validates input, calls ask_ai, and prints the result.
    """
    if len(sys.argv) != 2:
        print('❌ Usage error: python ask-ai.py "<text>"')
        return
    text = sys.argv[1]
    if not text.strip():
        print("❌ Error: No prompt text provided!")
        return
    result = ask_ai(text)
    print(result)


    # FIXME: 后台执行，不阻塞主进程

    B1,B2 = lcs_diff_align_desktop_info(text,result)
    write_diffs(B1,B2)
    # 调用 edge-tts 生成音频
    asyncio.run(generate_tts_audio(result, "output.mp3"))
    playsound("output.mp3", block=True)

if __name__ == "__main__":
    main()
