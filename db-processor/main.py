import os
import zmq
import sys
import ujson
import json
import yaml
from models import *
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

def load_schema():
	xquery_path = os.getcwd()+'/'+os.environ.get('schema','schema.yaml')
	with open(xquery_path) as file:
		xquery_data = yaml.load(file, Loader=yaml.FullLoader)
		order = []
		for i in xquery_data[0]['classes']:
			for j in i['attributes']:
				if "Required" not in j['value']:
					order.append(j['name'])
	return order

logger = logging.getLogger('main.py')

@db_session
def main(xquery_yaml_order):
	context = zmq.Context()
	socket = context.socket(zmq.PULL)

	logger.info('Connecting...')

	socket.connect("tcp://{}:{}".format(
		os.environ.get('ZMQ_GATEWAY_HOST', 'gateway-processor'), os.environ.get('ZMQ_GATEWAY_PORT1', 5555)
	))


	while True:
		try:
			msg = socket.recv()
			try:
				j = ujson.loads(msg)
			except Exception as e:
				logger.critical("Exception: ",exc_info=True)
				j = json.loads(msg)

			if j['topic'] == 'trades':
				for message in j['data']:
					try:

						item = XQuery(
							xquery_query_name = message['query_name'],
							xquery_chain_name = message['chain_name'],
							xquery_timestamp = int(message['timestamp']),
							xquery_tx_hash = message['tx_hash']
							)
					
						for o in xquery_yaml_order:
							for name, value in message.items():
								if o == f'xquery_{name.lower()}' and name.lower() not in ['query_name','chain_name','tx_hash','timestamp']:
									v = str(value)
									if o == 'xquery_timestamp':
										v = int(v)
									d = {f'xquery_{name.lower()}':v}
					
									item.set(**d)
				
						commit()
						logger.info(f'Logged: {message["tx_hash"]}')
					except Exception as e:
						logger.critical("Exception: ",exc_info=True)
		except Exception as e:
			logger.critical("Exception: ",exc_info=True)


if __name__ == "__main__":
	xquery_yaml_order = load_schema()
	main(xquery_yaml_order)
