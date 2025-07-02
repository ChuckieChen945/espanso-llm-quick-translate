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
import shutil
import subprocess
from typing import Tuple

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.extend([script_dir, os.path.join(script_dir, "lib")])
sys.stdout.reconfigure(encoding="utf-8")

from openai import OpenAI
from dotenv import load_dotenv

def ensure_env_file() -> None:
    """
    Ensures that a .env file exists. If not, tries to copy example.env to .env using shutil.copy.
    Raises FileNotFoundError if neither exists, lets OSError propagate on copy failure.
    """
    env_path = os.path.join(script_dir, ".env")
    example_env_path = os.path.join(script_dir, "example.env")

    if not os.path.exists(env_path):
        if os.path.exists(example_env_path):
            shutil.copy(example_env_path, env_path)
        else:
            raise FileNotFoundError(f"❌ Error: Missing .env file in directory: '{script_dir}'.")

def load_and_validate_env() -> Tuple[str, str, str, str, str,str, bool]:
    """
    Loads and validates .env configuration. Returns (api_key, base_url, model).
    Raises ValueError if any required variable is missing.
    """
    dotenv_path = os.path.join(script_dir, ".env")
    load_dotenv(dotenv_path)
    api_key = os.getenv("API_KEY")
    base_url = os.getenv("BASE_URL")
    model = os.getenv("MODEL")
    audio_path = os.getenv("AUDIO_FILE", os.path.join(script_dir, "translated.mp3"))
    diff_path = os.getenv("DIFF_FILE", os.path.join(script_dir, "diffs_text.txt"))
    sound_name = os.getenv("SOUND_NAME",  "en-GB-LibbyNeural")
    auto_play= os.getenv("AUTO_PLAY", "false")=='true'
    if not api_key:
        raise ValueError("❌ Error: API_KEY variable not found in .env file!")
    if not base_url:
        raise ValueError("❌ Error: BASE_URL variable not found in .env file!")
    if not model:
        raise ValueError("❌ Error: MODEL variable not found in .env file!")
    return api_key, base_url, model, audio_path, diff_path, sound_name, auto_play

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
        api_key, base_url, model, _ , _, _,_ = load_and_validate_env()
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



### ✅ Main logic ###

def spawn_background_task_cli(text, result, audio_file, diff_file, sound_name, auto_play):
    args = [
        sys.executable,  # ensures same Python interpreter
        os.path.join(script_dir,  "background_worker.py"),
        text,
        result,
        audio_file,
        diff_file,
        sound_name,
        'true'
    ]
    # subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.Popen(args)

def main() -> None:
    """
    Main entry point for the script. Parses arguments, validates input, calls ask_ai, and prints the result.
    """
    if len(sys.argv) != 2:
        print('❌ Usage error: python ask-ai.py "<text>"')
        return
    original = sys.argv[1]
    if not original.strip():
        print("❌ Error: No prompt text provided!")
        return
    translated = ask_ai(original)
    print(translated,flush=True)

    # ✅ Read paths from config and launch async background task
    _, _, _, audio_file, diff_file,sound_name,auto_play = load_and_validate_env()
    spawn_background_task_cli(original, translated, audio_file, diff_file,sound_name,auto_play)
    return

if __name__ == "__main__":
    main()
