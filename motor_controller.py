import time
import RPi.GPIO as GPIO
from rc_common.Direction import Turn, Motion
import motor_utils
from drv8833 import DRV8833, Pins, Direction, utils

# MARK - Pins
motor_pinA1 = 27  # left side of pi
motor_pinA2 = 22
turn_pinB1 = 23  # left side of pi
turn_pinB2 = 24

# MARK - Initial Frequencies
rear_freq = 20  # hz
# allows for more granular speed control than say,
# 300hz, also maybe consider using something like 50 hz b/c it is smoother

turn_freq = 10  # use lower hz for more torque, higher hz for more refined motor and higher speeds

# MARK - Speeds (Duty Cycles)
min_speed = 20.0  # duty cycle
max_speed = 90.0  # can actually go higher, like 100% duty cycle, but eh thats dangerous
turn_speed = 15
turn_slp_interval = 0.125

# MARK - speeds used for kickoff to have a better start up
kickoff_speed = 40
kickoff_freq = 10
last_kickoff = 0
kickoff_threshold = 3  # seconds

debug = True

default_pinmap = {
    Pins.AIN1: 27,
    Pins.AIN2: 22,
    Pins.BIN1: 23,
    Pins.BIN2: 24,
}

default_freqmap = {
    Pins.AIN1: rear_freq,
    Pins.AIN2: rear_freq,
    Pins.BIN1: turn_freq,
    Pins.BIN2: turn_freq,
}


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
