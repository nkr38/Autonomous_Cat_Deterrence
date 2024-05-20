from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput
from picamera2 import Picamera2
import libcamera
import numpy as np
import datetime
from pathlib import Path


class Camera:
    def __init__(
        self,
        main_size: tuple[int] = (1920, 1080),
        lores_size: tuple[int] = (192, 108),
        model_input_size: tuple[int] = (96, 96),
    ): 
        self.picam2 = Picamera2()
        self.encoder = H264Encoder()

        now = datetime.datetime.now().strftime("%H-%M-%S_%d-%m-%Y")
        # if Path("/media/raspi/catdrive/").is_dir():
        #     self.output = FfmpegOutput(f"/media/raspi/catdrive/vid_{now}.mp4")
        # else:
        self.output = FfmpegOutput(f"vid_{now}.mp4")
        
        self.fov = (102,67)
        self.fov = (90,67)
        self.fov = (80,67)

        self.main_size = main_size
        self.lores_size = lores_size
        self.vid_config = self.picam2.create_video_configuration(
            main={"size": main_size, "format": "RGB888"}, lores={"size": lores_size},
        )
        self.vid_config["transform"] = libcamera.Transform(vflip=1)

        self.picam2.configure(self.vid_config)

        self.model_input_size = model_input_size
        
        self.closed = True
        self.recording = False
    
    def __enter__(self):
        if self.picam2 is None:
            self.picam2 = Picamera2()
        self.closed = False
        return self
    def __exit__(self, type, value, traceback):
        if self.recording:
            self.stop_recording()
        self.picam2.stop()
        self.closed = True

    def start_recording(self):
        self.picam2.start_recording(self.encoder, self.output)
        self.recording = True

    def stop_recording(self):
        self.picam2.stop_recording()
        self.recording = False

    def greyscale(self, img: np.ndarray)-> np.ndarray: 
        return np.dot(img[..., :3], [0.2989, 0.5870, 0.1140])

    def capture_main(self, greyscale: bool = False) -> np.ndarray:
        if not self.recording:
            self.start_recording()
        cap = self.picam2.capture_array("main")
        return cap if not greyscale else self.greyscale(cap)

    def capture_lores(self, greyscale: bool = False) -> np.ndarray:
        if not self.recording:
            self.start_recording()
        cap = self.picam2.capture_array("lores")
        return cap if not greyscale else self.greyscale(cap)
