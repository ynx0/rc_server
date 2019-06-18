import socket
import time
import imagezmq.imagezmq as imagezmq

from imutils.video import VideoStream

IMAGE_SERVER_IP = '192.168.0.112'
IMAGE_SERVER_PORT = 27427

vs = VideoStream(usePiCamera=True)
sender = imagezmq.ImageSender(connect_to="tcp://{}:{}".format(IMAGE_SERVER_IP, IMAGE_SERVER_PORT))


# https://www.pyimagesearch.com/2019/04/15/live-video-streaming-over-network-with-opencv-and-imagezmq/
def start():
	vs.start()
	time.sleep(2)
	rpi_name = socket.gethostname()

	while True:
		frame = vs.read()
		sender.send_image(rpi_name, frame)
