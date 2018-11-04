import time
import RPi.GPIO as GPIO
from rc_common.Direction import Turn, Motion
import motor_utils as utils

# MARK - Pins
motor_pinA1 = 27  # left side of pi
motor_pinA2 = 22
turn_pinB1 = 23  # left side of pi
turn_pinB2 = 24

# MARK - Initial Frequencies
pwm_freq = 20  # hz, allows for more granular speed control than say, 300hz, also maybe consider using something like 50 hz b/c it is smoother
turn_freq = 10  # use lower hz for more torque, higher hz for more refined motor and higher speeds

# MARK - Speeds (Duty Cycles)
min_speed = 20.0  # duty cycle
max_speed = 45.0  # can actually go higher, like 100% duty cycle, but eh thats dangerous
turn_duty = 10
turn_slp_interval = 0.125

# MARK - speeds used for kickoff to have a better start up
kickoff_speed = 40
kickoff_freq = 10
last_kickoff = 0
kickoff_threshold = 3  # seconds

debug = True


class MotorController:

    def __init__(self):
        # motors
        self.motor1 = None
        self.motor2 = None
        self.turn1 = None
        self.turn2 = None

        # MARK - states
        self.current_direction = Turn.CENTER
        self.current_speed = 0  # duty cycle
        self.current_motor_freq = pwm_freq  # initial frequency
        self.current_motion_direction = Motion.STOPPED

        # MARK - misc
        self.last_kickoff = 0

        # MARK - defaults
        self.__default_freq = 20
        self.__default_speed = min_speed

    def setup(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(motor_pinA1, GPIO.OUT)
        GPIO.setup(motor_pinA2, GPIO.OUT)
        GPIO.setup(turn_pinB1, GPIO.OUT)
        GPIO.setup(turn_pinB2, GPIO.OUT)
        # https://electronics.stackexchange.com/a/80154/161902 for now going to

        self.motor1 = GPIO.PWM(motor_pinA1, pwm_freq)
        self.motor2 = GPIO.PWM(motor_pinA2, pwm_freq)
        self.turn1 = GPIO.PWM(turn_pinB1, turn_freq)
        self.turn2 = GPIO.PWM(turn_pinB2, turn_freq)
        self.motor1.start(0)
        self.motor2.start(0)
        self.turn1.start(0)
        self.turn2.start(0)

    # MARK - Helper methods

    @staticmethod
    def __normalize(speed):
        if speed > max_speed:
            speed = max_speed

        if speed < min_speed:
            speed = min_speed
        return speed

    @staticmethod
    def cleanup():
        GPIO.cleanup()
        print('\nexitting and cleaning up')

    @staticmethod
    def __stop(pwm: GPIO.PWM):
        pwm.ChangeDutyCycle(0)

    def __resetTurnPWMS(self):
        self.turn1.ChangeDutyCycle(0)
        self.turn2.ChangeDutyCycle(0)

    # MARK - Basic movement control methods
    def stopAll(self):
        self.__stop(self.motor1)
        self.__stop(self.motor2)
        self.current_speed = 0
        self.current_direction = Motion.STOPPED

    def forward(self, speed=min_speed):

        if debug: print('moving forward at speed: ' + str(speed))
        speed = self.__normalize(speed)
        self.kickoff()
        self.motor1.ChangeDutyCycle(speed)
        self.motor2.ChangeDutyCycle(0)
        self.current_speed = speed
        self.current_direction = Motion.FORWARD

    def backward(self, speed=min_speed):
        if debug: print('moving backwards at speed: ' + str(speed))
        speed = self.__normalize(speed)
        self.motor2.ChangeDutyCycle(speed)
        self.motor1.ChangeDutyCycle(0)
        self.current_speed = speed
        self.current_direction = Motion.BACKWARD

    def kickoff(self):
        kickoff_delta = time.time() - self.last_kickoff
        self.last_kickoff = time.time()

        if kickoff_delta <= 3:  # seconds
            self.motor1.ChangeDutyCycle(kickoff_speed)
            self.motor2.ChangeDutyCycle(0)
            self.changeRearFreq(kickoff_freq)
            time.sleep(0.75)
            self.resetRearFreq()
            self.last_kickoff = time.time()

    # MARK - Smooth movement

    def smoothStop(self):
        for speed in utils.__generate_smooth_stop(self.current_speed):
            self.forward(speed)

    def smoothForward(self, speed_ceil):
        for speed in utils.__generate_smooth(speed_ceil):
            self.forward(speed)

    def smoothBackward(self, speed_ceil):
        for speed in generate_smooth_backwards(speed_ceil):
            self.backward(speed)

    # MARK - Turning Methods

    def turn(self, pwm_turn: GPIO.PWM):
        self.__resetTurnPWMS()
        pwm_turn.ChangeDutyCycle(turn_duty)
        time.sleep(turn_slp_interval)
        pwm_turn.ChangeDutyCycle(0)

    def turnLeft(self):
        self.__resetTurnPWMS()
        self.__state_turn_left()
        self.turn(self.turn1)

    def turnRight(self):
        self.__resetTurnPWMS()
        self.__state_turn_right()
        self.turn(self.turn2)

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

    def turnToDirection(self, direction: Turn):

        delta_direction = abs(
            self.current_direction.value - direction.value)  # the math works this way because the way the values are setup
        direction_range = range(0, delta_direction)
        if direction is current_direction:
            if debug: print("direction to turn to is the same as the current direction")
        elif direction.is_left():
            for _ in direction_range:
                self.turnLeft()
        elif direction.is_right():
            for _ in direction_range:
                self.turnRight()

    def changeRearFreq(self, freq):
        self.motor1.ChangeFrequency(freq)
        self.motor2.ChangeFrequency(freq)

    def resetRearFreq(self):
        self.changeRearFreq(self.__default_freq)


if __name__ == '__main__':
    raise Exception("Error: Library file should not be run")
