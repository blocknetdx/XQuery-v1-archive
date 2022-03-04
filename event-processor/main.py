import os
import sys
import time
import signal
import atexit
import logging
import hashlib
import requests
import concurrent.futures
# from multiprocessing import JoinableQueue
from multiprocessing import Manager
# from queue import Queue
# from multiprocessing import Queue
# from multiprocessing.managers import BaseManager
from multiprocessing_logging import install_mp_handler
from web3 import Web3
from web3.middleware import local_filter_middleware, geth_poa_middleware
from engine.pinghandler import PingHandler
from eventhandler import EventHandler
from utils.zmq import ZMQ
from utils.liveness import *
from global_vars import GlobalVars

#configure logging
logging.basicConfig(
	level=logging.INFO,
	format="{asctime} {levelname:<8} {message}",
	style='{',
)
install_mp_handler()

# eventQueue = JoinableQueue()
# backeventQueue = JoinableQueue()
# zmqQueue = JoinableQueue()

# def get_eventqueue():
# 	global eventQueue
# 	return eventQueue
# def get_backeventqueue():
# 	global backeventQueue
# 	return backeventQueue
# def get_zmqqueue():
# 	global zmqQueue
# 	return zmqQueue	

# class MyManager(BaseManager): pass

# MyManager.register('GV',GlobalVars)
# MyManager.register('event_queue', callable=get_eventqueue)
# MyManager.register('backevent_queue', callable=get_backeventqueue)
# MyManager.register('zmq_queue', callable=get_zmqqueue)

# mm = MyManager()
# mm.start()

# gv = mm.GV()
# event_queue = mm.event_queue()
# backevent_queue = mm.backevent_queue()
# zmq_queue = mm.zmq_queue()
m = Manager()
event_queue = m.Queue()
backevent_queue = m.Queue()
zmq_queue = m.Queue()
gv = GlobalVars()

def start_process(zmq_queue, event_queue, CHAIN_HOST, event_type, gv):
	adapter = requests.adapters.HTTPAdapter(pool_connections=30, pool_maxsize=30)
	session = requests.Session()
	session.mount('http://', adapter)
	session.mount('https://', adapter)

	w2 = Web3(Web3.HTTPProvider(f'{CHAIN_HOST}', session=session, request_kwargs={'timeout': 60}))
	w2.middleware_onion.inject(geth_poa_middleware, layer=0)

	w3 = Web3(Web3.HTTPProvider(f'{CHAIN_HOST}', session=session, request_kwargs={'timeout': 60}))
	w3.middleware_onion.inject(geth_poa_middleware, layer=0)

	w4 = Web3(Web3.HTTPProvider(f'{CHAIN_HOST}', session=session, request_kwargs={'timeout': 60}))
	w4.middleware_onion.inject(geth_poa_middleware, layer=0)

	event_handler = EventHandler(w2, w3, w4, zmq_queue, event_queue, gv)

	if event_type == 'forward':
		event_handler.forward_loop(os.getpid())
	elif event_type == 'backward':
		event_handler.back_loop(os.getpid())
	elif event_type == 'process':
		event_handler.queue_handler(os.getpid())

def start_zmq(zmq_queue):
	zmq_handler = ZMQ(zmq_queue)
	ping_handler = PingHandler(zmq_handler)
	zmq_handler.init()
	ping_handler.start()
	zmq_handler.send_trades()

def main():
	logger = logging.getLogger('main.py')
	logger.info('Starting...')
	logger.info('Initializing global_vars...')

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

				logger.info('Starting Loop...')

				cpus = os.cpu_count()
				executor = concurrent.futures.ProcessPoolExecutor(max_workers=cpus)

				try:
					futures = []
					futures.append(executor.submit(start_zmq, zmq_queue))
					for i in range(0, cpus-1):
						if i in [0]:
							futures.append(executor.submit(start_process, zmq_queue, event_queue, CHAIN_HOST, 'forward', gv))
						elif i in [1]:
							futures.append(executor.submit(start_process, zmq_queue, backevent_queue, CHAIN_HOST, 'backward', gv))	
						elif i in list(range(int((cpus - 3)/2),int(cpus))):
							futures.append(executor.submit(start_process, zmq_queue, backevent_queue, CHAIN_HOST, 'process', gv))
						else:
							futures.append(executor.submit(start_process, zmq_queue, event_queue, CHAIN_HOST, 'process', gv))	
					while gv.return_key('running'):
						time.sleep(1)

					executor.shutdown(wait=True)
				except Exception as e:
					logger.critical("Closing...Exception: ", exc_info=True)
					executor.shutdown(wait=True)
				finally:
					executor.shutdown(wait=True)

		except Exception as e:
			logger.critical(f"Something went wrong when calling {CHAIN_NAME} host... Waiting 30 seconds", exc_info=True)
			time.sleep(30)

if __name__ == '__main__':
	main()