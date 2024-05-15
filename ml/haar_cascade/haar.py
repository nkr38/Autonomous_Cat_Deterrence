import cv2
from firmware.firmware import StepperMotor
from firmware.firmware import FireMechanism
import sys
sys.path.append("/home/raspi/Autonomous_Cat_Deterrence")
from time import sleep

from vision.Camera import Camera

# Classifier
faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalcatface.xml')

def get_angles(cam: Camera, loc: list or tuple or np.ndarray, input_size: tuple, xstep, ystep):
    x_inc = cam.fov[0] / input_size[0] * loc[0]
    y_inc = cam.fov[1] / input_size[1] * loc[1]
    x_angle = x_inc + xstep.angle
    y_angle = y_inc + ystep.angle
    if y_angle > 38:
        y_angle = 38
    elif y_angle < -40:
        y_angle = -40
    if x_angle > 90:
        x_angle = 90
    elif x_angle < -90:
        x_angle = -90
    return x_angle, y_angle

def picam_classifier(camera, runner):
    camera.start_recording()
    while not camera.closed and not runner.closed:
        img = camera.capture_lores()
        if img.size > 0:
            features, resized = get_features_from_image(img, camera.model_input_size)
            res = runner.classify(features)
            yield res, resized
    camera.stop_recording()


# Video capture source
cap = cv2.VideoCapture(2)
with Camera() as cam:
    with StepperMotor((17, 18, 27, 22), 2) as ystep, StepperMotor((5, 6, 12, 13), -3) as xstep:#, FireMechanism(26) as trigger:
        while True:

            # Capture frame
            # ret, frame = cap.read()
            cam.start_recording()
            frame = cam.capture_main()
            cam.stop_recording()


            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = faceCascade.detectMultiScale3(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE, outputRejectLevels=True)

            # Draw a rectangle and confidence
            for (x, y, w, h) in faces[0]:
                cv2.putText(frame, str(int(faces[2][0])) + '%', (x,y-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                # cv2.rectangle(frame, (0, 0), (20, 20), (255, 255, 0), 2)
                cv2.rectangle(frame, (cam.main_size[0]//2 + 5, cam.main_size[1]//2 + 5),(cam.main_size[0]//2 - 5, cam.main_size[1]//2 - 5), (255, 0, 255), 2)

                newx = x - cam.main_size[0]//2 + 1/2 * w
                newy = y - cam.main_size[1]//2 + 1/2 * h
                xangle, yangle = get_angles(cam, (newx, newy), gray.shape[:2], xstep, ystep)
                print(f"x = {newx}, y = {newy}")
                print(f"x_ang = {xangle}, y_ang = {yangle}")


                xstep.set_angle(-xangle)
                ystep.set_angle(-yangle)
                cv2.imshow("cat", frame)
                sleep(1)
                

            # Display the resulting frame live
            #cv2.imshow('Live Cat Detection', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

# When everything is done, release the capture
#cap.release()
cv2.destroyAllWindows()