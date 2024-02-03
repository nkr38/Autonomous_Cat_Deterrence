from firmware import StepperMotor

import time

def main():
    motor_pins = (17, 18, 27, 22)
    with StepperMotor(motor_pins) as stepper_motor:
        stepper_motor.step(stepper_motor.steps_per_revolution)
        print(stepper_motor.current_step, stepper_motor.angle)
        time.sleep(2)

if __name__ == '__main__':
    main()
