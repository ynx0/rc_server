import time
import RPi.GPIO as GPIO
from Direction import Turn, Motion


# MARK - Pins
motor_pinA1 = 27 # left side of pi
motor_pinA2 = 22
turn_pinB1 = 23 # left side of pi
turn_pinB2 = 24


# MARK - Initial Frequencies
pwm_freq = 20  # hz, allows for more granular speed control than say, 300hz, also maybe consider using something like 50 hz b/c it is smoother
turn_freq = 10 # use lower hz for more torque, higher hz for more refined motor and higher speeds

# MARK - Speeds (Duty Cycles)
min_speed = 20.0  # duty cycle
max_speed = 45.0  # can actually go higher, like 100% duty cycle, but eh thats dangerous
turn_duty = 30
turn_slp_interval = 0.125

# MARK - speeds used for kickoff to have a better start up
kickoff_speed = 40
kickoff_freq = 10
last_kickoff = 0
kickoff_threshold = 3 # seconds

# MARK - defaults
__default_freq = 20
__default_speed = min_speed

debug = True

# MARK - states
current_direction = Turn.CENTER
current_speed = 0 # duty cycle
current_motor_freq = pwm_freq # initial frequency

def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(motor_pinA1, GPIO.OUT)
    GPIO.setup(motor_pinA2, GPIO.OUT)
    GPIO.setup(turn_pinB1, GPIO.OUT)
    GPIO.setup(turn_pinB2, GPIO.OUT)
    # https://electronics.stackexchange.com/a/80154/161902 for now going to
    global motor1
    global motor2
    global turn1
    global turn2
    motor1 = GPIO.PWM(motor_pinA1, pwm_freq)
    motor2 = GPIO.PWM(motor_pinA2, pwm_freq)
    turn1 = GPIO.PWM(turn_pinB1, turn_freq)
    turn2 = GPIO.PWM(turn_pinB2, turn_freq)
    motor1.start(0)
    motor2.start(0)
    turn1.start(0)
    turn2.start(0)


current_motion_direction = Motion.STOPPED
# MARK - Helper methods

def __normalize(speed):
    if speed > max_speed:
        speed = max_speed

    if speed < min_speed:
        speed = min_speed
    return speed

def cleanup():
    GPIO.cleanup()
    print('\nexitting and cleaning up')

def __stop(pwm):
    pwm.ChangeDutyCycle(0)

def __resetTurnPWMS():
    turn1.ChangeDutyCycle(0)
    turn2.ChangeDutyCycle(0)

# MARK - Basic movement control methods
def stopAll():
    global current_speed
    global current_direction

    __stop(motor1)
    __stop(motor2)
    current_speed = 0
    current_direction = Motion.STOPPED

def forward(speed=min_speed):
    global current_speed
    global current_direction

    if debug: print('moving forward at speed: ' + str(speed))
    speed = __normalize(speed)
    kickoff()
    motor1.ChangeDutyCycle(speed)
    motor2.ChangeDutyCycle(0)
    current_speed = speed
    current_direction = Motion.FORWARD

def backward(speed=min_speed):
    global current_speed
    global current_direction

    if debug: print('moving backwards at speed: ' + str(speed))
    speed = __normalize(speed)
    motor2.ChangeDutyCycle(speed)
    motor1.ChangeDutyCycle(0)
    current_speed = speed
    current_direction = Motion.BACKWARD

def kickoff():
    global kickoff_speed
    global kickoff_freq
    global last_kickoff
    global kickoff_threshold

    kickoff_delta = time.time() - last_kickoff
    last_kickoff = time.time()
    if kickoff_delta <= 3: # seconds
        motor1.ChangeDutyCycle(kickoff_speed)
        motor2.ChangeDutyCycle(0)
        changeRearFreq(kickoff_freq)
        time.sleep(0.75)
        resetRearFreq()
        last_kickoff = time.time()

    else:
        pass



# MARK - Internal methods for speed generators

def __generate_smooth(ceil):
    return ((i * 10 ** exp) / 10000 for exp in range(2, 5) for i in range(1, ceil))

def __generate_smooth_stop(ceil):
    return reversed(list(__generate_smooth(ceil)))

def __generate_smooth_backwards(ceil):
    # its the same thing, but helps for code clarity
    return __generate_smooth_stop(ceil)


# MARK - Library methods that call internal methods

def smoothStop():
    for speed in __generate_smooth_stop(current_speed):
        forward(speed)

def smoothForward(speed_ceil):
    for speed in __generate_smooth(speed_ceil):
        forward(speed)

def smoothBackward(speed_ceil):
    for speed in generate_smooth_backwards(speed_ceil):
        backward(speed)


# MARK - Turning Methods


def turn(pwm_turn):
    __resetTurnPWMS()
    pwm_turn.ChangeDutyCycle(turn_duty)
    time.sleep(turn_slp_interval)
    pwm_turn.ChangeDutyCycle(0)

def turnLeft():
    __resetTurnPWMS()
    __state_turn_left()
    turn(turn1)

def turnRight():
    __resetTurnPWMS()
    __state_turn_right()
    turn(turn2)


def __state_turn_left():
    global current_direction # why do i need this :(
    print('current direction is: ' + current_direction.name)
    if current_direction is Turn.ABS_LEFT:
        if debug: print("Direction is already at ABS_LEFT")
    else:
        current_direction = Turn(current_direction.value - 1)

def __state_turn_right():
    global current_direction
    print('current direction is: ' + current_direction.name)
    if current_direction is Turn.ABS_LEFT:
        if debug: print("Direction is already at ABS_RIGHT")
    else:
        current_direction = Turn(current_direction.value + 1)

def turnToDirection(direction):
    global current_direction # just to be safe

    delta_direction = abs(current_direction.value - direction.value) # the math works this way because the way the values are setup
    direction_range = range(0, delta_direction)
    if direction is current_direction:
        if debug: print("direction to turn to is the same as the current direction")
    elif direction.is_left():
        for steps in direction_range:
            turnLeft()
    elif direction.is_right():
        for steps in direction_range:
            turnRight()

def changeRearFreq(freq):
    motor1.ChangeFrequency(freq)
    motor2.ChangeFrequency(freq)

def resetRearFreq():
    changeRearFreq(__default_freq)

if __name__ == '__main__':
    raise Exception("IdiocyException: Library file should not be run")
