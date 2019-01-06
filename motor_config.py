from drv8833 import Pins

# MARK - Pins
motor_pinA1 = 27  # left side of pi
motor_pinA2 = 22
turn_pinB1 = 23  # left side of pi
turn_pinB2 = 24


# MARK - Initial Frequencies
rear_freq = 20  # hz
turn_freq = 10  # use lower hz for more torque, higher hz for more refined motor and higher speeds

# allows for more granular speed control than say,
# 300hz, also maybe consider using something like 50 hz b/c it is smoother


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
    Pins.AIN1: motor_pinA1,
    Pins.AIN2: motor_pinA2,
    Pins.BIN1: turn_pinB1,
    Pins.BIN2: turn_pinB2,
}
default_freqmap = {
    Pins.AIN1: rear_freq,
    Pins.AIN2: rear_freq,
    Pins.BIN1: turn_freq,
    Pins.BIN2: turn_freq,
}