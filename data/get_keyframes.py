"""
Lev Saunders levsau00@gmail.com

For grabbing extracting a desired number of frames
from a video and saving them as images for use in 
ML training/validation


RUN FROM SCRIPT DIR
"""

# %%
import cv2
from pathlib import Path
import os

# %%
FPS = 5  # number of FPS to save
VID_DIR = Path("benchmark_vids")
OUT_DIR = Path("key_frames")

try:
    files = VID_DIR.glob("**/*.mp4")
except FileNotFoundError:
    print("video directory must be a directory")
    exit()

try:
    os.mkdir(OUT_DIR)
except OSError as error:
    print(error)

files = [x for x in files if x.is_file()]
# %%

for f in files:
    cap = cv2.VideoCapture(str(f))
    vid_fps = cap.get(cv2.CAP_PROP_FPS)
    stride = vid_fps // FPS
    success, img = cap.read()
    idx = 0
    count = 0
    while success:
        cv2.imwrite(f"{OUT_DIR}/{f.stem}_frame{count}.png", img)
        idx += stride
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        success, img = cap.read()
        count += 1

#%%