# %%
from Camera import Camera
from firmware.firmware import StepperMotor
import numpy as np
import random
from time import sleep

cat_loc = (30, 0)


def get_angles(cam: Camera, loc: list or tuple or np.ndarray):
    x_angle = cam.fov[0] / cam.model_input_size[0] * loc[0]
    y_angle = cam.fov[1] / cam.model_input_size[1] * loc[1]
    if y_angle > 38:
        y_angle = 38
    elif y_angle < -40:
        y_angle = -40
    return -x_angle, y_angle


# %%
with Camera() as cam, StepperMotor((17, 18, 27, 22), 2) as ystep, StepperMotor((5, 6, 12, 13), -3) as xstep:
    cat_loc = (
        random.randrange(
            -cam.model_input_size[0] // 2,
            random.randrange(cam.model_input_size[0] // 2),
        ),
        random.randrange(
            -cam.model_input_size[1] // 2,
            random.randrange(cam.model_input_size[1] // 2),
        ),
    )
    print(cat_loc)

    cam.picam2.start()
    cam.picam2.capture_file("before.jpg")

    print(get_angles(cam, cat_loc))
    angles = get_angles(cam, cat_loc)
    xstep.add_angle(angles[0])
    ystep.add_angle(angles[1])
    cam.picam2.capture_file("after.jpg")
    # pass
# %%
