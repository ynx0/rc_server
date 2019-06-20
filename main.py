import hardware_server


def main():
	print("Starting up servers")
	hardware_server.start()


if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print("Exitting")
