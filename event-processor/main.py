import os
import time
import logging
import requests
import sys
from multiprocessing import Manager
from multiprocessing import Process
from multiprocessing_logging import install_mp_handler
from eventhandler import start_process
from utils.zmq import start_zmq
from utils.liveness import *

#configure logging
logging.basicConfig(
	level=logging.INFO,
	format="{asctime} {levelname:<8} {message}",
	style='{',
)
install_mp_handler()

m = Manager()
event_queue = m.Queue()
backevent_queue = m.Queue()
zmq_queue = m.Queue()

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
			elif 'NEVM' in CHAIN_NAME:
				live = eth_live(CHAIN_HOST)
			if live == False:
				logger.info(f'{CHAIN_NAME} node syncing... Retrying in 30 seconds')
				time.sleep(30)
			elif live == True:
				logger.info(f'{CHAIN_NAME} node is live... Resuming')

				logger.info('Starting Loop...')

				cpus = os.cpu_count()
				# executor = concurrent.futures.ProcessPoolExecutor(max_workers=cpus)
				processes = []
				try:
					process = Process(target=start_zmq, args=(zmq_queue,))
					process.daemon = True
					process.start()
					processes.append(process)
					for i in range(0, cpus-1):
						if i in [0]:
							process = Process(target=start_process, args=(zmq_queue, event_queue, CHAIN_HOST, 'forward',))
							process.daemon = True
							process.start()
							processes.append(process)
						elif i in [1]:
							process = Process(target=start_process, args=(zmq_queue, backevent_queue, CHAIN_HOST, 'backward',))
							process.daemon = True
							process.start()
							processes.append(process)
						elif i in list(range(int((cpus - 3)/2),int(cpus))):
							process = Process(target=start_process, args=(zmq_queue, backevent_queue, CHAIN_HOST, 'process',))
							process.daemon = True
							process.start()
							processes.append(process)
						else:
							process = Process(target=start_process, args=(zmq_queue, event_queue, CHAIN_HOST, 'process',))
							process.daemon = True
							process.start()
							processes.append(process)
					while True:
						time.sleep(0.33)

					for p in processes:
						p.kill()
				except Exception as e:
					logger.critical("Closing...Exception: ", exc_info=True)
					for p in processes:
						p.kill()
				finally:
					logger.critical("Closing...")
					for p in processes:
						p.kill()

		except Exception as e:
			logger.critical(f"Something went wrong when calling {CHAIN_NAME} host... Waiting 30 seconds", exc_info=True)
			time.sleep(30)

if __name__ == '__main__':
	main()