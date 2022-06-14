import os
import json
import time
from web3 import Web3
import yaml
import json
import logging
import hashlib
import base64
import pickle5 as pickle
import random


class EventHandler:
	def __init__(self, web2: Web3, web3: Web3, web4: Web3, zmq_queue, event_queue, global_vars):
		self.logger = logging.getLogger("EventHandler")
		self.global_vars = global_vars
		self.chain_name = os.environ.get('NAME','AVAX')
		self.web2 = web2
		self.web3 = web3
		self.web4 = web4
		self.codec: ABICodec = web4.codec
		self.blockTime = {}
		self.event_queue = event_queue
		self.zmq_queue = zmq_queue
		self.query = self.load_query()
		self.index_topics = self.load_index_topics()
		self.abi = self.load_abi()
		self.rc_abi = self.load_rc_abi()
		self.topics = self.get_topics_for_query()
		self.address = self.get_address_filter_input()
		self.get_latest_block()
		self.initial_latest_block = self.latest_block
		self.start_block = self.load_start_block()
		#self.current_block = self.latest_block if self.global_vars.return_key('backblock_progress') == None else self.global_vars.return_key('backblock_progress')
		self.current_block = self.start_block if self.global_vars.return_key('backblock_progress') == None else self.global_vars.return_key('backblock_progress')
		self.current_block = self.latest_block if self.global_vars.return_key('backblock_progress') == None else self.global_vars.return_key('backblock_progress')
		#self.current_block_forward = self.latest_block if self.global_vars.return_key('forwardblock_progress') == None else self.global_vars.return_key('forwardblock_progress')
		self.current_block_forward = self.start_block if self.global_vars.return_key('forwardblock_progress') == None else self.global_vars.return_key('forwardblock_progress')
		self.lock_forward = False
		self.lock_backward = False
		self.lock_queue = False
		self.back_running = True
		self.running = True
		self.errors = 0

	def get_latest_block(self):
		self.latest_block = int(self.web4.eth.block_number)-1

	#load start_block if any
	def load_start_block(self):
		start_block = 'None'
		if 'historical' in list(self.query):
			sb = self.query['historical'][0]['fromBlock']
			start_block = int(sb) if sb.isdigit() else sb
		return start_block

	#get addresses filter if any
	def get_address_filter_input(self):
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

	#get token details from address
	def get_token_data(self, w3, address, abi):
		if address in self.global_vars.return_key('coin_data_cache'):
			return json.loads(pickle.loads(self.global_vars.return_key('coin_data_cache')[address]))
		else:
			contract = w3.eth.contract(address=Web3.toChecksumAddress(address),abi=abi)
			name = None
			symbol = None
			decimals = None
			try:
				name = contract.functions.name().call()
			except Exception as e:
				pass
			try:
				symbol = contract.functions.symbol().call()
			except Exception as e:
				pass
			try:
				decimals = contract.functions.decimals().call()
			except Exception as e:
				pass
			data =	{
			"name": str(name) if name else None,
			"symbol": str(symbol) if symbol else None,
			"decimals": int(decimals) if decimals else None
			}
			self.global_vars.remove_key('coin_data_cache')
			self.global_vars.add_key('coin_data_cache', address, pickle.dumps(pickle.PickleBuffer(json.dumps(data,sort_keys=True,ensure_ascii=True).encode('UTF-8')), protocol=5))
			return d

	#get pair details from contract address
	def get_tokens_from_caddress(self, w3, contract_address, abi):
		if contract_address in self.global_vars.return_key('token_data_cache'):
			return json.loads(pickle.loads(self.global_vars.return_key('token_data_cache')[contract_address]))
		else:
			contract = w3.eth.contract(address=Web3.toChecksumAddress(contract_address),abi=abi)
			token0_address = contract.functions.token0().call()
			token1_address = contract.functions.token1().call()
			token0 = self.get_token_data(w3, token0_address,abi)
			token1 = self.get_token_data(w3, token1_address,abi)
			data = {
			'token0': token0,
			'token1': token1
			}
			self.global_vars.remove_key('token_data_cache')
			self.global_vars.add_key('token_data_cache', contract_address, pickle.dumps(pickle.PickleBuffer(json.dumps(data,sort_keys=True,ensure_ascii=True).encode('UTF-8')), protocol=5))
			return data

	def get_address_filter(self, xquery_event):
		for address in self.address:
			for key, item in xquery_event.items():
				if isinstance(item, str) and address['address'] in item:
					return address
		return None


	def get_function(self, thread, w3, event_name, tx, contract_address, abi):
		function = {}
		transaction = w3.eth.get_transaction(tx)
		try:
			pb = contract_address.encode('UTF-8') + json.dumps(abi,sort_keys=True,ensure_ascii=True).encode('UTF-8')
			if pb in self.global_vars.return_key('functions_cache'):
				contract_router = self.global_vars.return_key('functions_cache')[pb]
			else:
				contract_router = w3.eth.contract(address=Web3.toChecksumAddress(contract_address), abi=abi)
				self.global_vars.remove_key('functions_cache')
				self.global_vars.add_key('functions_cache',pb,contract_router)

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
			pass
		return function

	def process_event(self, thread, w3, event, event_name, event_type, contract_address, abi):
		xquery_event = {}
		try:
			pb = contract_address.encode('UTF-8') + json.dumps(abi,sort_keys=True,ensure_ascii=True).encode('UTF-8')
			if pb in self.global_vars.return_key('contracts_cache'):
				contract = self.global_vars.return_key('contracts_cache')[pb]
			else:
				contract = w3.eth.contract(address=Web3.toChecksumAddress(contract_address), abi=abi)				
				self.global_vars.remove_key('contracts_cache')
				self.global_vars.add_key('contracts_cache', pb, contract)
			contract_call = getattr(contract,f'{event_type.lower()}s')
			action_call = getattr(contract_call,event_name.lower().capitalize())
			xquery_event = action_call().processLog(event)
			xquery_event = json.loads(Web3.toJSON(xquery_event))
		except Exception as e:
			pass
		return xquery_event

	def process_event_args(self, thread, w3, xquery_name, xquery_event, contract_address, abi):
		args = {}
		try:
			for arg in list(xquery_event['args']):
				args[arg] = xquery_event['args'][arg]
			del args['args']
		except Exception as e:
			pass
		try:
			if xquery_name == 'Swap':
				tokens = self.get_tokens_from_caddress(w3, xquery_event['address'], self.rc_abi['abi'])
				for key, item in tokens.items():
					for key1, item1 in item.items():
						args[f'{key}_{key1}'] = item1
				#check side
				if args['amount0Out'] == 0:
					args['side'] = 'sell'
				elif args['amount1Out'] == 0:
					args['side'] = 'buy'				
			else:
				token_data = self.get_token_data(w3, contract_address, self.rc_abi['abi'])
				args['token0_name'] = token_data['name']
				args['token0_symbol'] = token_data['symbol']
				args['token0_decimals'] = token_data['decimals']
		except Exception as e:
			pass
		return args

	def control_loop(self):
		while self.running and self.errors <2:
			time.sleep(1)

	#listen loop for incoming events | backward listner
	def forward_loop(self, thread):
		self.logger.info(f'{thread} Starting forward listener...')
		SLEEP_TIME_BEFORE_INDEXING_NEXT_BLOCK = 0.01  # This variable is used to reduce CPU load after old blocks are indexed
		
		while self.running and self.errors < 2:
			if not self.lock_forward:
				try:
					self.logger.info(f'{thread} {self.chain_name} {self.current_block_forward} FORWARD')
					forward_filter = self.web2.eth.filter({
						'fromBlock': hex(self.current_block_forward-1),
						'toBlock': hex(self.current_block_forward)
					})
					for event in forward_filter.get_all_entries():
						self.event_queue.put(event)
					self.web2.eth.uninstall_filter(forward_filter.filter_id)
					self.lock_forward = True
					if self.current_block_forward >= self.initial_latest_block: # This if condition will allow faster indexing of old blocks
						self.get_latest_block()
						if self.current_block_forward >= self.latest_block:
							SLEEP_TIME_BEFORE_INDEXING_NEXT_BLOCK = 0.5
					self.current_block_forward = self.current_block_forward + 1 if self.current_block_forward < self.latest_block else self.latest_block
					self.global_vars.update_key('forwardblock_progress', self.current_block_forward)
					self.lock_forward = False
					time.sleep(SLEEP_TIME_BEFORE_INDEXING_NEXT_BLOCK)
				except ValueError as e:
					self.logger.critical('ValueError in Listener loop!',exc_info=True)
				except Exception as e:
					self.logger.critical('Exception in Listener loop!',exc_info=True)
					self.errors += 0.2
					if self.errors > 2:
						self.running = False
						self.global_vars.update_key('running', False)

#	def back_loop(self, thread):
#		self.logger.info(f'{thread} Starting back listener...')
#		while self.back_running and self.errors < 2:
#			if not self.lock_backward:
#				try:
#					if self.start_block != 'None':
#						#if self.current_block>self.start_block:
#						if self.current_block<self.latest_block:
#							self.logger.info(f'{thread} {self.chain_name} {self.current_block} BACKWARD')
#							backward_filter = self.web2.eth.filter({
#									#'fromBlock': hex(int(self.current_block)-1),
#									#'toBlock': hex(int(self.current_block))
#									'fromBlock': hex(int(self.current_block)),
#									'toBlock': hex(int(self.current_block)+1)
#								})
#							for event in backward_filter.get_all_entries():
#								self.event_queue.put(event)
#							self.web2.eth.uninstall_filter(backward_filter.filter_id)
#							self.lock_backward = True
#							#self.current_block = self.current_block - 1 if self.current_block > self.start_block else self.start_block
#							self.current_block = self.current_block + 1 if self.current_block < self.latest_block else self.latest_block
#							self.global_vars.update_key('backblock_progress', self.current_block)
#							self.lock_backward = False
#					else:
#						self.back_running = False
#					time.sleep(0.01)
#				except ValueError as e:
#					self.logger.critical('ValueError in Back Listener loop!',exc_info=True)
#				except Exception as e:
#					self.logger.critical('Exception in Back Listener loop!',exc_info=True)
#					self.errors += 0.2
#					if self.errors > 2:
#						self.back_running = False

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
				event = self.event_queue.get()
				tx = event.transactionHash.hex()
				address = event['address']
				event_topics = event['topics']
				main_topic = [x.hex() for x in event_topics][0] if len(event_topics)>0 else None
				event_hash = hashlib.sha256(json.dumps(Web3.toJSON(event), sort_keys=True, ensure_ascii=True).encode('UTF-8')).hexdigest()

				if main_topic in self.topics and event_hash not in self.global_vars.return_key('events_cache'):
					while self.lock_queue==True:
						time.sleep(1)
					self.lock_queue = True
					self.global_vars.add_key('events_cache', event_hash, None)
					self.global_vars.remove_key('events_cache')
					self.lock_queue = False
					xquery_type = [_type for _type in list(self.index_topics) for index_topic in self.index_topics[_type] if index_topic['topic'] == main_topic][0]
					xquery_name = [index_topic['name'] for _type in list(self.index_topics) for index_topic in self.index_topics[_type] if index_topic['topic'] == main_topic][0]

					blockNumber = event['blockNumber']

					retries = 0
					while blockNumber not in self.blockTime:
						try:
							timestamp = self.web4.eth.getBlock(blockNumber)
							if 'timestamp' in timestamp:
								self.blockTime[blockNumber] = timestamp['timestamp']
						except Exception as e:
							pass

						if retries > 10:
							break

						retries += 1
						time.sleep(0.01)
					if retries > 10:
						continue

					timestamp = self.blockTime[blockNumber]

					try:
						#process event
						xquery_event = self.process_event(thread, self.web4, event, xquery_name, xquery_type, address, self.rc_abi['abi'])

						xquery_event['chain_name'] = self.chain_name.split('_')[0]
						xquery_event['query_name'] = xquery_name
						xquery_event['tx_hash'] = tx
						xquery_event['timestamp'] = timestamp
						xquery_event['blocknumber'] = int(blockNumber)
					
						#process args
						args = self.process_event_args(thread, self.web4, xquery_name, xquery_event, address, self.rc_abi['abi'])
						for k, v in args.items():
							xquery_event[f'{k}'] = v

						#check address filter
						address_filter = self.get_address_filter(xquery_event)
						if address_filter:
							xquery_event['address_filter'] = address_filter['name']

						#get function
						function = self.get_function(thread, self.web4, xquery_name, tx, address, self.abi['abi'])
						if len(list(function)) == 0:
							function = self.get_function(thread, self.web4, xquery_name, tx, address, self.rc_abi['abi'])
							if len(list(function)) == 0 and address_filter!=None:
								function = self.get_function(thread, self.web4, xquery_name, tx, address_filter['address'], self.abi['abi'])
						for k, v in function.items():
							xquery_event[f'{k}'] = v

						#add to db only if event belongs to a router
						if 'address_filter' in list(xquery_event):
							xquery_event['xhash'] = hashlib.sha256(json.dumps(xquery_event, sort_keys=False, ensure_ascii=True).encode('UTF-8')).hexdigest()
							self.logger.info(f"{thread} SUCCESS QUERY:{xquery_name} XHASH:{xquery_event['xhash']} TX:{tx}")
							self.zmq_queue.put([xquery_event])
					except Exception as e:
						self.logger.critical(f"Exception Worker {thread} Type: {xquery_type} Name: {xquery_name} TX: {tx}",exc_info=True)
				self.event_queue.task_done()
			except Exception as e:
				self.logger.critical(f'Exception in worker: {thread}',exc_info=True)

				self.running = False
				self.global_vars.update_key('running', False)
				self.errors += 1
