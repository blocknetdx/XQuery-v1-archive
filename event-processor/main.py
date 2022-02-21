import os
import sys
import time
import signal
import atexit
import concurrent.futures
from concurrent.futures import thread
from web3 import Web3
from web3.middleware import local_filter_middleware, geth_poa_middleware
from engine.pinghandler import PingHandler
from eventhandler import EventHandler
from utils.zmq import zmq_handler
from utils.liveness import *
import logging
import hashlib

logging.basicConfig(
	level=logging.INFO,
	format="{asctime} {levelname:<8} {message}",
	style='{',
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
	WORKER_THREADS = int(os.environ.get('WORKER_THREADS', 20))

	CHAIN_NAME = os.environ.get('NAME', 'ETH')
	
	while True:
		try:
			if 'ETH' in CHAIN_NAME:
				live = eth_live(CHAIN_HOST)
			elif 'AVAX' in CHAIN_NAME:
				live = avax_live(CHAIN_HOST)
			if live == False:
				logger.info(f'{CHAIN_NAME} node syncing... Retrying in 30 seconds')
				time.sleep(30)
			elif live == True:
				logger.info(f'{CHAIN_NAME} node is live... Resuming')
		
				w2 = Web3(Web3.HTTPProvider('{}'.format(CHAIN_HOST)))
				w2.middleware_onion.inject(geth_poa_middleware, layer=0)

				w3 = Web3(Web3.HTTPProvider('{}'.format(CHAIN_HOST)))
				w3.middleware_onion.inject(geth_poa_middleware, layer=0)

				w4 = Web3(Web3.HTTPProvider('{}'.format(CHAIN_HOST)))
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
						if i == 1:
							futures.append(executor.submit(event_handler.back_loop, thread=i))
						else:	
							futures.append(executor.submit(event_handler.queue_handler, thread=i))
					event_handler.loop()

					executor._threads.clear()  
					thread._threads_queues.clear()
					executor.shutdown(wait=False)
					# sys.exit(1)
				except Exception as e:
					logger.critical("Closing...Exception: ", exc_info=True)
					zmq_handler.disconnect()
					executor._threads.clear()
					thread._threads_queues.clear()
					executor.shutdown(wait=False)
					# sys.exit(1)
				finally:
					zmq_handler.disconnect()
					executor._threads.clear()
					thread._threads_queues.clear()
					executor.shutdown(wait=False)
					# sys.exit(1)

		except Exception as e:
			logger.info(f"Something went wrong when calling {CHAIN_NAME} host...")


	

if __name__ == '__main__':
	main()
