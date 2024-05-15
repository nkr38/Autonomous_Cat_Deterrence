import RPi.GPIO as GPIO

import atexit
import time

class StepperMotor:
    def __init__(self, motor_pins: tuple[int], gear_ratio: float = 1):
        self._motor_pins = motor_pins
        self._gear_ratio = gear_ratio

        self._speed_variation_ratio: float = 1/64
        self._stride_angle: float = 5.625
        self.step_sequence: list[list[int]] = [[1,0,0,1],
                                               [1,0,0,0],
                                               [1,1,0,0],
                                               [0,1,0,0],
                                               [0,1,1,0],
                                               [0,0,1,0],
                                               [0,0,1,1],
                                               [0,0,0,1]]

        self._current_step: int = 0

        GPIO.setup(motor_pins, GPIO.OUT)
        GPIO.output(motor_pins, GPIO.LOW)

    def __enter__(self):
        self._initial_context_step = self.current_step
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.set_step(self._initial_context_step)

    @property
    def angles_per_step(self) -> float:
        return self._stride_angle * self._speed_variation_ratio

    @property
    def steps_per_revolution(self) -> int:
        return int(360 / self.angles_per_step)

    @property
    def current_step(self) -> int:
        return self._current_step

    @property
    def angle(self) -> float:
        return self.current_step * self.angles_per_step / self._gear_ratio

    # rotates the server a specified number of steps
    # number_of_steps: the number if steps to spin
    #                  if number_of_steps > 0: clockwise
    #                  if number_of_steps < 0: counter clockwise
    # time_between_steps: the amount of time to wait between each step
    # Lowering this enough will cease to work at the servo's physical limitation
    def step(self, number_of_steps: int, time_between_steps: float = 0.001):
        step_inc = 1 if number_of_steps > 0 else -1
        number_of_steps = abs(number_of_steps)

        for i in range(number_of_steps):
            self._current_step = self.current_step + step_inc
            GPIO.output(self._motor_pins, self.step_sequence[self.current_step % len(self.step_sequence)])
            time.sleep(time_between_steps)

    def set_step(self, step: int, time_between_steps: float = 0.001):
        number_of_steps = step - self.current_step
        self.step(number_of_steps, time_between_steps)

    def set_angle(self, angle: float, time_between_steps: float = 0.001):
        angle *= self._gear_ratio

        step = int(angle / self.angles_per_step)
        self.set_step(step, time_between_steps)

    def add_angle(self, angle: float, time_between_steps: float = 0.001):
        self.set_angle(self.angle + angle)

class FireMechanism:
    def __init__(self, pin):
        self._pin = pin

        GPIO.setup(self._pin, GPIO.OUT)
        GPIO.output(self._pin, GPIO.LOW)

    def fire(self):
        GPIO.output(self._pin, GPIO.HIGH)
        time.sleep(0.50)
        GPIO.output(self._pin, GPIO.LOW)

class MotionSensor:
    def __init__(self, pin):
        self._pin = pin

        GPIO.setup(self._pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def is_motion(self):
        return GPIO.input(self._pin)

class Gimble:
    def __init__(self, pitch_pins, yaw_pins, fire_pin, motion_sensor_pin):
        self.pitch_motor = StepperMotor(pitch_pins, 2)
        self.yaw_motor = StepperMotor(yaw_pins, -3)
        self.fire_mechanism = FireMechanism(fire_pin)
        # self.motion_sensor = MotionSensor(motion_sensor_pin)

GPIO.setmode(GPIO.BCM)
atexit.register(GPIO.cleanup)
