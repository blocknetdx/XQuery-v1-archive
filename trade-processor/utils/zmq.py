import json
import os
import time
import uuid
import zmq
from queue import Queue
import logging

class ZMQ:
	def __init__(self):
		self.logger = logging.getLogger("ZMQ")
		self.context = zmq.Context()
		self.socket = self.context.socket(zmq.PUSH)
		self.socket.setsockopt(zmq.LINGER, 0)
		self.sub_socket = self.context.socket(zmq.PULL)

		self.logger.info('Connecting...')

		self.sub_socket.connect("tcp://{}:{}".format(
			os.environ.get('ZMQ_GATEWAY_HOST', 'gateway-processor'), os.environ.get('ZMQ_GATEWAY_PORT1', 5555)
		))

		self.socket.connect("tcp://{}:{}".format(
			os.environ.get('ZMQ_GATEWAY_HOST', 'gateway-processor'),
			os.environ.get('ZMQ_GATEWAY_PORT2', 5556)))

		self.exchange = os.environ.get('EXCHANGE', 'AVAX')
		self.id = uuid.uuid4().hex
		self.queue = Queue()

	def init(self):
		try:
			self.logger.info('Initializing Connection')

			time.sleep(1)

			connect_data = {
				'topic': 'connect',
				'data': {
					'id': self.id,
				}
			}
			self.logger.info('Trying Connection', connect_data)

			self.socket.send_json(connect_data)

		except Exception as e:
			self.logger.critical('ZMQ HANDLER', exc_info=True)

	def ping(self):
		connect_data = {
			'topic': 'ping',
			'data': {
				'id': self.id,
			}
		}

		self.logger.info('Ping', connect_data)

		try:
			self.socket.send_json(connect_data)
		except Exception as e:
			self.logger.critical(e,exc_info=true)

	def disconnect(self):
		connect_data = {
			'topic': 'disconnect',
			'data': {
				'id': self.id,
			}
		}

		self.logger.info('Disconnecting', connect_data)

		try:
			self.socket.send_json(connect_data)
		except Exception as e:
			self.logger.critical(e,exc_info=True)

	def insert_queue(self, trades):
		self.queue.put(trades)

	def send_trades(self):
		while True:
			try:
				events = self.queue.get()

				self.socket.send_json({
					'topic': 'trades',
					'data': events
				})

				self.queue.task_done()
			except Exception as e:
				self.logger.critical('ZMQ HANDLER', exc_info=True)


zmq_handler = ZMQ()
