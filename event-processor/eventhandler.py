import os
import json
import time
from queue import Queue
from web3 import Web3
from utils.zmq import zmq_handler
import yaml
import json
import logging

token_data = dict()

class EventHandler:
	def __init__(self, web2: Web3, web3: Web3, web4: Web3, latest_block):
		self.logger = logging.getLogger("EventHandler")
		self.chain_name = os.environ.get('NAME','AVAX')
		self.web2 = web2
		self.web3 = web3
		self.web4 = web4
		self.codec: ABICodec = web4.codec
		self.blockTime = {}
		self.queue = Queue()
		self.query = self.load_query()
		self.index_topics = self.load_index_topics()
		self.abi = self.load_abi()
		self.rc_abi = self.load_rc_abi()
		self.topics = self.get_topics_for_query()
		self.address = self.get_address_filter()
		self.latest_block = int(latest_block) if latest_block.isdigit() else latest_block
		self.current_block = int(latest_block) if latest_block.isdigit() else int(latest_block)
		self.start_block = self.load_start_block()
		self.running = True
		self.errors = 0

	#load start_block if any
	def load_start_block(self):
		start_block = 'None'
		if 'historical' in list(self.query):
			sb = self.query['historical'][0]['fromBlock']
			start_block = int(sb) if sb.isdigit() else sb
		return start_block

	#get addresses filter if any
	def get_address_filter(self):
		addresses = []
		if 'address' in list(self.query):
			for address in self.query['address']:
				addresses.append(address)
		return addresses


	#get topics for query events or functions comparing with index_topics generated from abi
	def get_topics_for_query(self):
		topics = []
		for to_query in self.query['query']:
			name = to_query['name']
			for _type in list(self.index_topics):
				for index_topic in self.index_topics[_type]:
					if index_topic['name'] == name:
						topics.append(index_topic['topic'])
		return topics

	#get token details from address
	def get_token_data(self, address):
		contract = self.web4.eth.contract(address=Web3.toChecksumAddress(address),abi=self.rc_abi['abi'])
		name = contract.functions.name().call()
		symbol = contract.functions.symbol().call()
		decimals = contract.functions.decimals().call()
		return {
		"name": str(name),
		"symbol": str(symbol),
		"decimals": str(decimals)
		}

	#get pair details from contract address
	def get_tokens_from_caddress(self, contract_address):
		global token_data
		if contract_address in token_data:
			return token_data[contract_address]
		else:
			contract = self.web4.eth.contract(address=contract_address,abi=self.rc_abi['abi'])
			token0_address = contract.functions.token0().call()
			token1_address = contract.functions.token1().call()
			token0 = self.get_token_data(token0_address)
			token1 = self.get_token_data(token1_address)
			data = {
			'token0': token0,
			'token1': token1
			}
			token_data[contract_address] = data
			return data

	#load index topics from file
	def load_index_topics(self):
		index_topics_path = os.getcwd()+'/index_topics.yaml'
		with open(index_topics_path) as file:
			index_topics = yaml.load(file, Loader=yaml.FullLoader)
			return index_topics

	#loading abi from file
	def load_abi(self):
		abi_path = os.getcwd()+'/'+os.environ.get('ABI_FILE','abi.json')
		with open(abi_path) as file:
			abi = json.load(file)
			return abi

	#loading xRC20 abi from file
	def load_rc_abi(self):
		abi_path = os.getcwd()+'/'+os.environ.get('ABI_FILE','RC20.json')
		with open(abi_path) as file:
			abi = json.load(file)
			return abi

	#loading data from query.yaml
	def load_query(self):
		query_path = os.getcwd()+'/'+os.environ.get('query','query.yaml')
		with open(query_path) as file:
			query_data = yaml.load(file, Loader=yaml.FullLoader)
			for entry in query_data['chains']:
				if entry['name'] == self.chain_name: 
					return entry

	#listen loop for incoming events | backward listner
	def loop(self):
		self.logger.info('Starting listener...')

		forward_filter = self.web3.eth.filter({
			'toBlock': 'latest'
		})

		while self.running:
			try:
				for event in forward_filter.get_new_entries():
					self.queue.put(event)

				#backward loop events
				if self.start_block != 'None':
					if self.current_block>self.start_block:
						backward_filter = self.web3.eth.filter({
								'fromBlock': hex(int(self.current_block)-1),
								'toBlock': hex(int(self.current_block)),
							})
						for event in backward_filter.get_all_entries():
							self.queue.put(event)
						self.current_block = self.current_block - 2 if self.current_block > self.start_block else self.start_block
				time.sleep(0.01)
			except ValueError as e:
				self.logger.critical('ValueError in Listener loop!',exc_info=True)
				
				forward_filter = self.web3.eth.filter({
					'toBlock': 'latest',
				})
			except Exception as e:
				self.logger.critical('Exception in Listener loop!',exc_info=True)
				self.errors += 0.2

	def queue_handler(self, thread):
		self.logger.info('Starting Worker: {}'.format(thread))

		while self.running:
			if len(self.blockTime) > 100:
				try:
					del self.blockTime
					self.blockTime = {}
				except Exception as e:
					self.logger.critical('Exception while attempting to reset blocktimes',exc_info=True)

			try:
				event = self.queue.get()
				tx = event.transactionHash.hex()
				address = event['address']
				event_topics = event['topics']
				main_topic = [x.hex() for x in event_topics][0]

				if main_topic in self.topics:
					xquery_type = [_type for _type in list(self.index_topics) for index_topic in self.index_topics[_type] if index_topic['topic'] == main_topic][0]
					xquery_name = [index_topic['name'] for _type in list(self.index_topics) for index_topic in self.index_topics[_type] if index_topic['topic'] == main_topic][0]

					contract = self.web3.eth.contract(address=address, abi=self.rc_abi['abi'])
					transaction = self.web4.eth.get_transaction(tx)
					function = {}
					try:
						contract_router = self.web4.eth.contract(address=address, abi=self.abi['abi'])
						decoded_input = contract_router.decode_function_input(transaction.input)
						func = decoded_input[0]
						func_data = decoded_input[1]
						function["fn_name"] = func.__dict__['fn_name']
						for k, v in func_data.items():
							if not isinstance(v, list):
								function[k] = str(v)
							else:
								function[k] = ','.join(v)
					except Exception as e:
						self.logger.exception(f"Worker {thread} {xquery_name} Failed to get function data for TX {tx}")
						# self.logger.critical(f"Worker {thread} {xquery_name} Failed to get function data for TX {tx}",exc_info=True)

					blockNumber = event['blockNumber']

					retries = 0
					while blockNumber not in self.blockTime:
						try:
							timestamp = self.web4.eth.getBlock(blockNumber)
							if 'timestamp' in timestamp:
								self.blockTime[blockNumber] = timestamp['timestamp']
						except Exception as e:
							self.logger.critical('Exception while waiting for block time!', exc_info=True)

						if retries > 10:
							break

						retries += 1
						time.sleep(0.01)
					if retries > 10:
						continue

					timestamp = self.blockTime[blockNumber]

					try:
						contract_call = getattr(contract,f'{xquery_type.lower()}s')
						action_call = getattr(contract_call,xquery_name.lower().capitalize())
						swap_events = action_call().processLog(event)
						swap_events = json.loads(Web3.toJSON(swap_events))
						swap_events['chain_name'] = self.chain_name.split('_')[0]
						swap_events['query_name'] = xquery_name
						swap_events['tx_hash'] = tx
						swap_events['timestamp'] = timestamp
						swap_events['blocknumber'] = int(blockNumber)
						for arg in list(swap_events['args']):
							swap_events[arg] = swap_events['args'][arg]
						del swap_events['args']
						try:
							if xquery_name == 'Swap':
								tokens = self.get_tokens_from_caddress(swap_events['address'])
								for key, item in tokens.items():
									for key1, item1 in item.items():
										swap_events[f'{key}_{key1}'] = item1
								#check side
								if swap_events['amount0Out'] == 0:
									swap_events['side'] = 'sell'
								elif swap_events['amount1Out'] == 0:
									swap_events['side'] = 'buy'
								#check address filter
								for address in self.address:
									for key, item in swap_events.items():
										if item == address['address']:
											swap_events['address_filter'] = address['name']
											break
									break
							else:
								swap_events['token0_name'] = contract.functions.name().call()
								swap_events['token0_symbol'] = contract.functions.symbol().call()
								swap_events['token0_decimals'] = contract.functions.decimals().call()
							for k, v in function.items():
								swap_events[f'{k}'] = v
						except Exception as e:
							self.logger.critical('Exception ',exc_info=True)
						if 'address_filter' in list(swap_events):
							self.logger.info(f"Worker {thread} Type: {xquery_type} Name: {xquery_name}")
							zmq_handler.insert_queue([swap_events])
						# else:
						# 	self.queue.task_done()
					except Exception as e:
						self.logger.critical("Exception: ",exc_info=True)
					self.queue.task_done()
			except Exception as e:
				self.logger.critical(f'Exception in worker: {thread}',exc_info=True)

				self.running = False
				self.errors += 1
