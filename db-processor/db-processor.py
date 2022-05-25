import os
import zmq
import sys
import ujson
import json
import yaml
from models import *
import logging

logging.basicConfig(
	level=logging.INFO,
	format="{asctime} {levelname:<8} {message}",
	style='{',
)

def load_schema():
	xquery_path = os.getcwd()+'/'+os.environ.get('schema','schema.yaml')
	with open(xquery_path) as file:
		xquery_data = yaml.load(file, Loader=yaml.FullLoader)
		order = []
		for i in xquery_data[0]['classes']:
			for j in i['attributes']:
				if "Required" not in j['value']:
					order.append([j['name'],j['value']])
	return order

logger = logging.getLogger('db-processor.py')


@db_session
def main(xquery_yaml_order):
	context = zmq.Context()
	# socket = context.socket(zmq.PULL)
	socket = context.socket(zmq.SUB)
	socket.setsockopt_string(zmq.SUBSCRIBE, "")
	socket.set_hwm(0)

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
				logger.critical("Exception ujson")
				j = json.loads(msg)

			if j['topic'] == 'trades':
				for message in j['data']:
					try:
						logger.info(f'RECEIVED QUERY:{message["query_name"]} XHASH:{message["xhash"]} TX:{message["tx_hash"]}')
						item = XQuery(
							xquery_query_name = message['query_name'],
							xquery_chain_name = message['chain_name'],
							xquery_timestamp = int(message['timestamp']),
							xquery_tx_hash = message['tx_hash'],
							xquery_xhash = message['xhash'],
							xquery_blocknumber = int(message['blocknumber'])
							)
					
						for o in xquery_yaml_order:
							for name, value in message.items():
								if o[0] == f'xquery_{name.lower()}' and name.lower() not in ['query_name','blocknumber','chain_name','tx_hash','timestamp','xhash']:
									if value and value !='':
										if 'str' in o[1].lower():
											v = str(value)
										elif 'decimal' in o[1].lower():
											v = int(str(value),0)
										elif 'bool' in o[1].lower():
											if value.lower() in ['true','t']:
												v = True
											else:
												v = False
										d = {f'xquery_{name.lower()}':v}
										item.set(**d)
						parsed = item.to_dict()
						for o in xquery_yaml_order:
							if o[0] not in list(parsed):
								d = {o[0]:None}
								item.set(**d)
						commit()
						logger.info(f'LOGGED QUERY:{message["query_name"]} XHASH:{message["xhash"]} TX:{message["tx_hash"]}')
					except Exception as e:
						logger.critical("Exception: ",exc_info=True)
		except Exception as e:
			logger.critical("Exception: ",exc_info=True)


if __name__ == "__main__":
	xquery_yaml_order = load_schema()
	main(xquery_yaml_order)
