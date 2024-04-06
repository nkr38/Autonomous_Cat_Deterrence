# %%
import cv2
import os
import sys, getopt
import signal
import time
import numpy as np
import math
from edge_impulse_linux.image import ImageImpulseRunner

# Local Imports
sys.path.append("/home/raspi/Autonomous_Cat_Deterrence")
from vision.Camera import Camera


modelfile = (
    "/home/raspi/Autonomous_Cat_Deterrence/ml/fomo/models/catfomo2-linux-aarch64-v3.eim"
)
# If you have multiple webcams, replace None with the camera port you desire, get_webcams() can help find this
camera_port = None


runner = None
# if you don't want to see a camera preview, set this to False
show_camera = True
if sys.platform == "linux" and not os.environ.get("DISPLAY"):
    show_camera = False


def now():
    return round(time.time() * 1000)


def get_webcams():
    port_ids = []
    for port in range(5):
        print("Looking for a camera in port %s:" % port)
        camera = cv2.VideoCapture(port)
        if camera.isOpened():
            ret = camera.read()[0]
            if ret:
                backendName = camera.getBackendName()
                w = camera.get(3)
                h = camera.get(4)
                print(
                    "Camera %s (%s x %s) found in port %s " % (backendName, h, w, port)
                )
                port_ids.append(port)
            camera.release()
    return port_ids


def picam_classifier(camera, runner):
    camera.start_recording()
    while not camera.closed and not runner.closed:
        img = camera.capture_lores()
        if img.size > 0:
            features, resized = get_features_from_image(img, camera.model_input_size)
            res = runner.classify(features)
            yield res, resized
    camera.stop_recording()


def get_features_from_image(img, input_size):
    features = np.array([])

    input_w = input_size[0]
    input_h = input_size[1]

    in_frame_cols = img.shape[1]
    in_frame_rows = img.shape[0]

    factor_w = input_w / in_frame_cols
    factor_h = input_h / in_frame_rows

    resize_size_w = int(math.ceil(factor_w * in_frame_cols))
    resize_size_h = int(math.ceil(factor_h * in_frame_rows))
    # One dim will match the classifier size, the other will be larger
    resize_size = (resize_size_w, resize_size_h)

    img = cv2.cvtColor(img, cv2.COLOR_YUV420p2RGB)
    resized = cv2.resize(img, resize_size, interpolation=cv2.INTER_AREA)

    pixels = np.array(resized).flatten()

    for ix in range(0, len(pixels), 3):
        rgb = pixels[ix:ix+3]
        features = np.append(features, (rgb[0] << 16) + (rgb[1] << 8) + rgb[2])
    return features.tolist(), resized


def sigint_handler(sig, frame):
    print("Interrupted")
    if runner:
        runner.stop()
    sys.exit(0)


signal.signal(signal.SIGINT, sigint_handler)


print("MODEL: " + modelfile)


with ImageImpulseRunner(modelfile) as runner, Camera() as camera:
    try:
        model_info = runner.init()
        print(
            'Loaded runner for "'
            + model_info["project"]["owner"]
            + " / "
            + model_info["project"]["name"]
            + '"'
        )
        labels = model_info["model_parameters"]["labels"]
        # if camera_port:
        #     videoCaptureDeviceId = int(args[1])
        # else:
        #     port_ids = get_webcams()
        #     if len(port_ids) == 0:
        #         raise Exception("Cannot find any webcams")
        #     if len(port_ids) > 1:
        #         raise Exception(
        #             "Multiple cameras found. Add the camera port ID as a second argument to use to this script"
        #         )
        #     videoCaptureDeviceId = int(port_ids[0])

        # camera = cv2.VideoCapture(videoCaptureDeviceId)
        # camera = get_picam()
        camera.start_recording()
        ret = camera.capture_lores()
        if ret.size > 0:
            w, h = camera.lores_size

            print(
                f"Camera ~>  main:{camera.main_size}  lores:{camera.lores_size} selected."
            )
            camera.stop_recording()
        else:
            print("No image from camera")
            camera.stop_recording()
            sys.exit(1)

        next_frame = 0  # limit to ~10 fps here
    
        for res, img in picam_classifier(camera, runner):
            thresh_bb = []

            # if next_frame > now():
            #     time.sleep((next_frame - now()) / 1000)

            if "bounding_boxes" in res["result"].keys():
                for bb in res["result"]["bounding_boxes"]:
                    if bb['value'] > 0.7:
                        thresh_bb.append(bb)
                print(
                    "Found %d bounding boxes (%d ms.)"
                    % (
                        len(thresh_bb),
                        res["timing"]["dsp"] + res["timing"]["classification"],
                    )
                )
                for bb in thresh_bb:
                    print(
                        "\t%s (%.2f): x=%d y=%d w=%d h=%d"
                        % (
                            bb["label"],
                            bb["value"],
                            bb["x"],
                            bb["y"],
                            bb["width"],
                            bb["height"],
                        )
                    )
                    img = cv2.rectangle(
                        img,
                        (bb["x"], bb["y"]),
                        (bb["x"] + bb["width"], bb["y"] + bb["height"]),
                        (255, 0, 0),
                        1,
                    )
            if show_camera:
                im2 = cv2.resize(img, dsize=(400, 400))
                cv2.imshow("edgeimpulse", cv2.cvtColor(im2, cv2.COLOR_RGB2BGR))
                print(
                    "Found %d bounding boxes (%d ms.)"
                    % (
                        len(thresh_bb),
                        res["timing"]["dsp"] + res["timing"]["classification"],
                    )
                )
                if cv2.waitKey(1) == ord("q"):
                    break

            next_frame = now() + 100
    finally:
        if runner:
            runner.stop()
