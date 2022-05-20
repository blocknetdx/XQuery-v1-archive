import random

class GlobalVars:
	def __init__(self):
		self.queue = False
		self.running = True
		self.backblock_progress = None
		self.forwardblock_progress = None
		self.token_data_cache = dict()
		self.coin_data_cache = dict()
		self.functions_cache = dict()
		self.contracts_cache = dict()
		self.events_cache = list()

	def return_key(self, key):
		if key == 'queue':
			return self.queue
		elif key == 'running':
			return self.running
		elif key == 'backblock_progress':
			return self.backblock_progress
		elif key == 'forwardblock_progress':
			return self.forwardblock_progress
		elif key == 'token_data_cache':
			return self.token_data_cache
		elif key == 'coin_data_cache':
			return self.coin_data_cache
		elif key == 'functions_cache':
			return self.functions_cache
		elif key == 'contracts_cache':
			return self.contracts_cache
		elif key == 'events_cache':
			return self.events_cache

	def update_key(self, key, value):
		if key == 'queue':
			self.queue = value
		elif key == 'running':
			self.running = value
		elif key == 'backblock_progress':
			self.backblock_progress = value
		elif key == 'forwardblock_progress':
			self.forwardblock_progress = value

	def add_key(self, key, value, value1):
		if key == 'token_data_cache':
			self.token_data_cache[value] = value1
		elif key == 'coin_data_cache':
			self.coin_data_cache[value] = value1
		elif key == 'functions_cache':
			self.functions_cache[value] = value1
		elif key == 'contracts_cache':
			self.contracts_cache[value] = value1
		elif key == 'events_cache':
			self.events_cache.insert(0, value)

	def remove_key(self, key):
		if key == 'token_data_cache' and len(self.token_data_cache.keys())>=100:
			self.token_data_cache.pop(random.choice(self.token_data_cache.keys()))
		elif key == 'coin_data_cache' and len(self.coin_data_cache.keys())>=100:
			self.coin_data_cache.pop(random.choice(self.coin_data_cache.keys()))
		elif key == 'functions_cache' and len(self.functions_cache.keys())>=100:
			self.functions_cache.pop(random.choice(self.functions_cache.keys()))
		elif key == 'contracts_cache' and len(self.contracts_cache.keys())>=100:
			self.contracts_cache.pop(random.choice(self.contracts_cache.keys()))
		elif key == 'events_cache' and len(self.events_cache)>=100:
			self.events_cache.pop()