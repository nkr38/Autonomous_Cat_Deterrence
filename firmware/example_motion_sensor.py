from firmware import MotionSensor

import time

def main():
    motion_sensor = MotionSensor(26)

    while True:
        print("motion:", 1 if motion_sensor.is_motion() else 0)
        time.sleep(0.1)

if __name__ == '__main__':
    main()
