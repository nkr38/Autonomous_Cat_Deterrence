from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput
from picamera2 import Picamera2
import numpy as np
from pathlib import Path


class Camera:
    def __init__(
        self,
        outpath: str | Path = "test.mp4",
        main_size: tuple[int] = (1920, 1080),
        lores_size: tuple[int] = (192, 108),
        model_input_size: tuple[int] = (92, 92),
    ):
        self.picam2 = Picamera2()
        self.encoder = H264Encoder()
        self.output = FfmpegOutput(outpath)

        self.vid_config = self.picam2.create_video_configuration(
            main={"size": main_size}, lores={"size": lores_size}
        )
        self.picam2.configure(self.vid_config)

        self.model_input_size = model_input_size

    def start_recording(self):
        self.picam2.start_recording(self.encoder, self.output)

    def stop_recording(self):
        self.picam2.stop_recording()

    def greyscale(self, img: np.ndarray):
        return np.dot(img[..., :3], [0.2989, 0.5870, 0.1140])

    def capture_main(self, greyscale: bool = False) -> np.ndarray:
        cap = self.picam2.capture_array("main")
        return cap if not greyscale else self.greyscale(cap)

    def capture_lores(self, greyscale: bool = False) -> np.ndarray:
        cap = self.picam2.capture_array("lores")
        return cap if not greyscale else self.greyscale(cap)
