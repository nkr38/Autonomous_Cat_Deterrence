import cv2
from firmware.firmware import StepperMotor, FireMechanism, MotionSensor
from app.db import *
import sys
sys.path.append("/home/raspi/Autonomous_Cat_Deterrence")
from time import sleep, time
import numpy as np
from vision.Camera import Camera
import datetime
import atexit

VERBOSE = True
ENABLED = True
SERIAL_NUMBER = 1225357956
# Classifier
faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalcatface.xml')
db = DataBase()
db.connect_DB()

def capture_and_sense(cam: Camera):
    frame = cam.capture_main()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale3(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE, outputRejectLevels=True)
    return faces, frame, gray


def get_angles(cam: Camera, loc: list or tuple or np.ndarray, input_size: tuple, x_step, y_step):
    x_inc = cam.fov[0] / input_size[0] * loc[0]
    y_inc = cam.fov[1] / input_size[1] * loc[1]
    x_angle = x_inc + x_step.angle
    y_angle = y_inc + y_step.angle
    if y_angle > 38:
        y_angle = 38
    elif y_angle < -40:
        y_angle = -40
    if x_angle > 90:
        x_angle = 90
    elif x_angle < -90:
        x_angle = -90
    return x_inc, y_inc

def dist_to_center(x_centered, y_centered):
    return np.sqrt((x_centered)**2 + (y_centered)**2) 

def search_and_fire(cam: Camera):  
    time_last_seen = 0
    with StepperMotor((9, 11, 25, 8), 2) as y_step, StepperMotor((5, 6, 12, 13), -3) as x_step:
        trigger = FireMechanism(26)
        print("Entering Main Loop")
        while True:
            # Capture frame
            print("captured frame")
            faces, frame, gray = capture_and_sense(cam)
            
            # Draw a rectangle and confidence
            if len(faces[0]) > 0:
                # print(faces[0][0].flatten())
                time_last_seen = time()
                if VERBOSE:
                    print("cat face seen")
                x, y, w, h = faces[0][0].flatten().tolist()

                cv2.putText(frame, f"{faces[2][0]:.2f} %", (x,y-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                # cv2.rectangle(frame, (0, 0), (20, 20), (255, 255, 0), 2)
                cv2.rectangle(frame, (cam.main_size[0]//2 + 5, cam.main_size[1]//2 + 5),(cam.main_size[0]//2 - 5, cam.main_size[1]//2 - 5), (255, 0, 255), 2)

                x_centered = x - cam.main_size[0]//2 + 1/2 * w
                y_centered = y - cam.main_size[1]//2 + 1/2 * h

                if dist_to_center(x_centered, y_centered) <= 30:
                    center_count += 10
                    if center_count >= 3:
                        if VERBOSE:
                            print("FIRING and sleeping for 3 secs...")
                        now = datetime.datetime.now()
                        db.add_rows('detection', {'serial_number': SERIAL_NUMBER, 'detection_datetime': now})

                        trigger.fire(0.3)
                        trigger.fire(0.2)

                        sleep(3)
                else:
                    center_count = 0
                x_angle, y_angle = get_angles(cam, (x_centered, y_centered), gray.shape[:2], x_step, y_step)
                # print(f"x = {x_centered}, y = {y_centered}")
                # print(f"x_ang = {x_angle}, y_ang = {y_angle}")


                x_step.add_angle(-x_angle*3/5)
                y_step.add_angle(-y_angle*3/5)
                #cv2.imshow("cat", frame)

                sleep(0.5)
                
            else:
                if time_last_seen == 0:
                    continue
                elif time() - time_last_seen > 10:
                    break
    if VERBOSE:
        print("Going to sleep")
    sleep(3)



if __name__ == "__main__":
    motion_sensor = MotionSensor(2)
    with Camera(main_size=(960,540)) as cam:
        try:
            while True:
                if motion_sensor.is_motion() and ENABLED:
                    if VERBOSE:
                        print("Motion Detected!")
                    search_and_fire(cam)

                    # Check disabled flag
                    sqlStatement = """SELECT * FROM device WHERE serial_number = ?"""
                    parameters = (SERIAL_NUMBER,)
                    records = db.get_one(sqlStatement, parameters=parameters)
                    if records[2] == 0:
                        ENABLED = False
                    else:
                        ENABLED = True
                sleep(0.5)
        except KeyboardInterrupt:
            cam.stop_recording()
            sys.exit(0)

# When everything is done, release the capture
cv2.destroyAllWindows()
