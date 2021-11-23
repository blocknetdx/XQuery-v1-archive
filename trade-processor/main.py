import os
import sys
import time
import signal
import atexit
# import threading
import concurrent.futures
from concurrent.futures import thread
from web3 import Web3
from web3.middleware import local_filter_middleware, geth_poa_middleware
from engine.pinghandler import PingHandler
from eventhandler import EventHandler
# from uniswap.token import Tokens
# from utils.uniswap.tokens import tokens
from utils.zmq import zmq_handler

import logging
from logging.handlers import RotatingFileHandler, MemoryHandler

rfh = RotatingFileHandler(
	filename='%slog' % __file__[:-2],
	mode='a',
	maxBytes=20*1024*1024,
	backupCount=2,
	encoding=None,
	delay=0
) 

stdout = logging.StreamHandler(sys.stdout)
mm = MemoryHandler(4096,flushLevel=logging.INFO,target=stdout,flushOnClose=True)

logging.basicConfig(
	level=logging.INFO,
	format="{asctime} {levelname:<8} {message}",
	style='{',
	handlers=[
		rfh,
		mm
	]
)

def on_exit():
	zmq_handler.disconnect()


signal.signal(signal.SIGTERM, on_exit)
signal.signal(signal.SIGSEGV, on_exit)
atexit.register(on_exit)


def main():
	logger = logging.getLogger('main.py')
	logger.info('Starting...')

	zmq_handler.init()

	CHAIN_HOST = os.environ.get('CHAIN_HOST', 'https://api.avax.network/ext/bc/C/rpc')
	CHAIN_PORT = os.environ.get('CHAIN_PORT','None')
	CHAIN_HOST = CHAIN_HOST+':'+CHAIN_PORT if CHAIN_PORT!='None' else CHAIN_HOST
	WORKER_THREADS = int(os.environ.get('WORKER_THREADS', 20))

	w2 = Web3(Web3.HTTPProvider('{}'.format(CHAIN_HOST)))
	# w3.middleware_onion.add(local_filter_middleware)
	w2.middleware_onion.inject(geth_poa_middleware, layer=0)

	w3 = Web3(Web3.HTTPProvider('{}'.format(CHAIN_HOST)))
	# w3.middleware_onion.add(local_filter_middleware)
	w3.middleware_onion.inject(geth_poa_middleware, layer=0)

	w4 = Web3(Web3.HTTPProvider('{}'.format(CHAIN_HOST)))
	# w4.middleware_onion.add(local_filter_middleware)
	w4.middleware_onion.inject(geth_poa_middleware, layer=0)
	LATEST_BLOCK = str(w4.eth.getBlock('latest').number)

	logger.info('Starting Loop...')
	event_handler = EventHandler(w2, w3, w4, LATEST_BLOCK)

	try:
		ping_handler = PingHandler(zmq_handler)

		executor = concurrent.futures.ThreadPoolExecutor()

		futures = []
		futures.append(executor.submit(zmq_handler.send_trades))

		ping_handler.start()

		for i in range(0, WORKER_THREADS):
			futures.append(executor.submit(event_handler.queue_handler, thread=i))

		event_handler.loop()

		executor._threads.clear()  
		thread._threads_queues.clear()
		executor.shutdown(wait=False)
		sys.exit(1)
	except Exception as e:
		# print(e)
		logger.critical("Exception: ", exc_info=True)
		zmq_handler.disconnect()
		executor._threads.clear()
		thread._threads_queues.clear()
		executor.shutdown(wait=False)
		sys.exit(1)
	finally:
		zmq_handler.disconnect()
		executor._threads.clear()
		thread._threads_queues.clear()
		executor.shutdown(wait=False)
		sys.exit(1)

if __name__ == '__main__':
	main()
