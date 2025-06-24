
import os
import sys

parent_folder_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(parent_folder_path)
sys.path.append(os.path.join(parent_folder_path, "lib"))

from playsound import playsound

if __name__ == "__main__":
    playsound("output.mp3", block=True)
