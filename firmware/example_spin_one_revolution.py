from firmware import StepperMotor

import time

def main():
    with StepperMotor((17, 18, 27, 22), 2) as pitch_motor, StepperMotor((5, 6, 12, 13), -3) as yaw_motor:
        while True:
            cmd_text = input()
            args = cmd_text.split(' ')
            direction = args[0]
            angle = int(args[1])

            if direction == "r":
                yaw_motor.add_angle(angle)
            elif direction == "l":
                yaw_motor.add_angle(-angle)
            elif direction == "u":
                pitch_motor.add_angle(angle)
            elif direction == "d":
                pitch_motor.add_angle(-angle)
            else:
                print("invalid direction")

            print("pitch:", pitch_motor.angle)
            print("yaw:", yaw_motor.angle)

        pitch_motor.set_angle(-90)
        while True:
            pitch_motor.step(2)
            yaw_motor.step(5)
            print(pitch_motor.current_step, pitch_motor.angle)
            print(yaw_motor.current_step, yaw_motor.angle)
            time.sleep(0.001)

if __name__ == '__main__':
    main()
