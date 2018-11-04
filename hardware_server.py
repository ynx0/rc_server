import sys
from procbridge.procbridge import *
from motor_controller import MotorController
from rc_common import netcfg
from rc_common.RC_Commands import Commands  # yeah i know, its not pretty

# get outward facing ip (credit: someone on SO)
host = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [
    [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in
     [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]

port = 9939
mc = MotorController()


def movement_handler(command, args):
    print("Command is: %s" % str(command))
    print("Args are: %s" % str(args))

    if command == Commands.FORWARD:
        mc.forward(args['speed'])
    elif command == Commands.BACKWARD:
        mc.backward(args['speed'])
    elif command == Commands.LEFT:
        mc.turnLeft()
    elif command == Commands.RIGHT:
        mc.turnRight()
    elif command == Commands.STOP:
        mc.stopAll()
    elif command == Commands.SHUTDOWN:
        mc.stopAll()
        mc.cleanup()
        server.stop()
        sys.exit(0)
    else:
        print("Error: Unknown command: " + command)


server = ProcBridgeServer(host, netcfg.HDW_PORT, movement_handler)


def start():
    mc.setup()
    server.start()
    # the only way to indefinitely keep open the server.
    while True:
        pass


if __name__ == '__main__':
    try:
        start()
    except KeyboardInterrupt:
        mc.stopAll()
        server.stop()
        print("Stopping server...")
