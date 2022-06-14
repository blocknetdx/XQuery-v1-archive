import time
from threading import Thread

class PingHandler(Thread):
    def __init__(self, zmq_handler):
        super().__init__()

        self.zmq_handler = zmq_handler
        self.running = False
        self.errors = 0

    def run(self):
        while self.running:
            self.zmq_handler.ping()
            time.sleep(15)

