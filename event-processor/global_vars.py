
def init():
	global token_data
	global coin_data
	global backblock_progress
	global forwardblock_progress
	global events_cache
	global functions_cache
	global contracts_cache
	global events_cache
	global queue
	global running
	queue = False
	running = True
	backblock_progress = None
	forwardblock_progress = None
	token_data_cache = dict()
	coin_data_cache = dict()
	functions_cache = dict()
	contracts_cache = dict()
	events_cache = list()