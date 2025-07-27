"""Play audio.

package.yml 定义了 <Ctrl-Q> 快捷键，用于播放音频。

这个文件的作用是，在 package.yml 中被调用，用于播放音频。
以及被 background_worker.py 根据配置中是否自动播放调用。
"""

import os
import sys

parent_folder_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(parent_folder_path)
sys.path.append(os.path.join(parent_folder_path, "lib"))

from playsound import playsound

if __name__ == "__main__":
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    playsound("translated.mp3", block=True)
    print()
