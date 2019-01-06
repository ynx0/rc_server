import time
import RPi.GPIO as GPIO

from motor_config import *
from rc_common.Direction import Turn, Motion
import motor_utils
from drv8833 import DRV8833, Direction, utils


# noinspection PyPep8Naming
class MotorController:

    def __init__(self, pinmap, freqmap):
        self.pinmap = pinmap or default_pinmap
        self.freqmap = freqmap or default_freqmap

        self.DRV8833 = DRV8833(pinmode=GPIO.BCM, pinmap=self.pinmap, freqmap=self.freqmap)

        # MARK - states
        self.current_direction = Turn.CENTER
        self.current_speed = 0  # duty cycle
        self.current_motor_freq = rear_freq  # initial frequency
        self.current_motion_direction = Motion.STOPPED

        # MARK - misc
        self.last_kickoff = 0

        # MARK - defaults
        self.__default_rear_freq = rear_freq
        self.__default_speed = min_speed
        self.__default_turn_freq = turn_freq

    # MARK - Helper methods


    def __resetTurnPWMS(self):
        self.DRV8833.set_motor_b(0, Direction.FORWARD)

    # MARK - Basic movement control methods
    def stopAll(self):
        self.DRV8833.stop_all()
        self.current_speed = 0
        self.current_direction = Motion.STOPPED

    def forward(self, speed=min_speed):
        speed = utils.clamp(speed, max_speed, min_speed)
        if debug: print('moving forward at normalized speed: ' + str(speed))
        # kickoff commented out because it was interfering with xbox controls
        # self.kickoff()
        self.DRV8833.set_motor_a(speed, Direction.FORWARD)
        self.current_speed = speed
        self.current_direction = Motion.FORWARD

    def backward(self, speed=min_speed):
        speed = utils.clamp(speed, max_speed, min_speed)
        if debug: print('moving backwards at normalized speed: ' + str(speed))

        self.DRV8833.set_motor_a(speed, Direction.BACKWARD)

        self.current_speed = speed
        self.current_direction = Motion.BACKWARD

    def kickoff(self):
        kickoff_delta = time.time() - self.last_kickoff
        self.last_kickoff = time.time()

        if kickoff_delta <= 3:  # seconds
            self.DRV8833.set_motor_a(kickoff_speed, Direction.FORWARD)
            self.changeRearFreq(kickoff_freq)
            time.sleep(0.75)
            self.resetRearFreq()
            self.last_kickoff = time.time()

    # MARK - Smooth movement

    def smoothStop(self):
        for speed in motor_utils.generate_smooth_stop(self.current_speed):
            self.forward(speed)

    def smoothForward(self, speed_ceil):
        for speed in motor_utils.generate_smooth(speed_ceil):
            self.forward(speed)

    def smoothBackward(self, speed_ceil):
        for speed in motor_utils.generate_smooth_backwards(speed_ceil):
            self.backward(speed)

    # MARK - Turning Methods

    def turn(self, direction: Direction):
        self.__resetTurnPWMS()
        # pwm_turn.ChangeDutyCycle(turn_duty)
        self.DRV8833.set_motor_b(turn_speed, direction)
        time.sleep(turn_slp_interval)
        self.DRV8833.stop_motor_b()
        # pwm_turn.ChangeDutyCycle(0)

    def turnLeft(self):
        self.__state_turn_left()
        self.turn(Direction.FORWARD)  # TODO TESTME!!!!!

    def turnRight(self):
        self.__state_turn_right()
        self.turn(Direction.BACKWARD)  # TODO TESTME!!!!!

    # noinspection PyTypeChecker
    def __state_turn_left(self):
        print('current direction is: ' + self.current_direction.name)
        if self.current_direction is Turn.ABS_LEFT:
            if debug: print("Direction is already at ABS_LEFT")
        else:
            self.current_direction = Turn(self.current_direction.value - 1)

    # noinspection PyTypeChecker
    def __state_turn_right(self):
        print('current direction is: ' + self.current_direction.name)
        if self.current_direction is Turn.ABS_RIGHT:
            if debug: print("Direction is already at ABS_RIGHT")
        else:
            self.current_direction = Turn(self.current_direction.value + 1)


    def changeRearFreq(self, freq):
        self.DRV8833.change_frequency_a(freq)

    def resetRearFreq(self):
        self.changeRearFreq(self.__default_rear_freq)

    def changeFrontFreq(self, freq):
        self.DRV8833.change_frequency_b(freq)

    def resetFrontFreq(self):
        self.changeFrontFreq(self.__default_turn_freq)


if __name__ == '__main__':
    raise Exception("Error: Library file should not be run")
