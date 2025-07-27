"""_summary_.

Raises
------
    FileNotFoundError: _description_
    ValueError: _description_
    ValueError: _description_
    ValueError: _description_

Returns
-------
    _type_: _description_
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


# TODO: 重构代码，弃用.env文件进行配置，改用 项目 根目录下的 .espanso-llm-quick-translate.json 文件进行配置
# TODO: 将 ensure_env_file() load_and_validate_env() 等功能合并成一个专门管理配置的类
def ensure_env_file() -> None:
    """Ensure that a .env file exists.

     If not, tries to copy example.env to .env using shutil.copy.
    Raises FileNotFoundError if neither exists, lets OSError propagate on copy failure.
    """
    env_path = Path(__file__).parent / ".env"
    example_env_path = Path(__file__).parent / "example.env"

    if not env_path.exists():
        if example_env_path.exists():
            shutil.copy(example_env_path, env_path)
        else:
            msg = f"❌ Error: Missing .env file in directory: '{Path(__file__).parent}'."
            raise FileNotFoundError(
                msg,
            )


def load_and_validate_env() -> tuple[str, str, str, str, str, str, bool, str]:
    """
    Load and validates .env configuration.

    Returns (api_key, base_url, model).
    Raises ValueError if any required variable is missing.
    """
    dotenv_path = Path(__file__).parent / ".env"
    load_dotenv(dotenv_path)
    api_key = os.getenv("API_KEY")
    base_url = os.getenv("BASE_URL")
    model = os.getenv("MODEL")
    audio_path = os.getenv("AUDIO_FILE", Path(__file__).parent / "translated.mp3")
    diff_path = os.getenv("DIFF_FILE", Path(__file__).parent / "diffs_text.txt")
    sound_name = os.getenv("SOUND_NAME", "en-GB-LibbyNeural")
    auto_play = os.getenv("AUTO_PLAY", "false") == "true"
    target_language = os.getenv("TARGET_LANGUAGE", "English")
    if not api_key:
        msg = "❌ Error: API_KEY variable not found in .env file!"
        raise ValueError(msg)
    if not base_url:
        msg = "❌ Error: BASE_URL variable not found in .env file!"
        raise ValueError(msg)
    if not model:
        msg = "❌ Error: MODEL variable not found in .env file!"
        raise ValueError(msg)
    return api_key, base_url, model, audio_path, diff_path, sound_name, auto_play, target_language


def ask_ai(text: str) -> str:
    """
    Send a prompt to a local or remote LLM using the OpenAI API interface and returns the response.

    Args:
        text (str): The user prompt to send to the LLM.

    Returns
    -------
        str: The LLM's response or an error message.
    """
    try:
        ensure_env_file()
        api_key, base_url, model, _, _, _, _, target_language = load_and_validate_env()
        try:
            with Path.open("system_prompt.txt", encoding="utf-8") as f:
                system_prompt = f.read()
        except FileNotFoundError:
            print("Error: The file 'your_file.txt' was not found.")
        except Exception as e:
            print(f"An error occurred: {e}")
        client = OpenAI(api_key=api_key, base_url=base_url)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    # TODO： 改用 from string import Template 来替换
                    "content": system_prompt.replace(r"${TARGET_LANGUAG}", target_language),
                },
                {
                    "role": "user",
                    "content": text,
                },
            ],
            stream=False,
        )
        # TODO: 调用 background worker
        return response.choices[0].message.content.strip()
    except Exception:
        return "❌ Error: An unexpected error occurred while processing your request. Check model name, api key etc... and try again later."


### ✅ Main logic ###
