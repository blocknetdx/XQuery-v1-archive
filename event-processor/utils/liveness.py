import requests

def eth_live(HOST):
	try:
		payload = {'jsonrpc': '2.0', 'method': 'eth_syncing', 'params': [], 'id': 1}
		headers = {'Content-Type':'application/json'}
		resp = requests.post(HOST,headers=headers,json=payload)
		data = resp.json()
		if data['result'] == False:
			return True
		else:
			return False
	except Exception as e:
		return False

def avax_live(HOST):
	try:
		payload = {'jsonrpc': '2.0', 'id': 1, 'method': 'info.isBootstrapped', 'params': {'chain': 'C'}}
		headers = {'Content-Type':'application/json'}
		resp = requests.post(HOST.split('/ext')[0]+'/ext/info',headers=headers,json=payload)
		data = resp.json()
		if data['result']['isBootstrapped'] == True:
			return True
		else:
			return False
	except Exception as e:
		return False

def nevm_live(HOST):
	try:
		payload = {'jsonrpc': '2.0', 'method': 'eth_blockNumber', 'params': [], 'id': 1}
		headers = {'Content-Type':'application/json'}
		resp = requests.post(HOST,headers=headers,json=payload)
		data = resp.json()
		if data['result'] < hex(107659):  # 107659 is the NEVM block number now. (Little hack)
			return False
		else:
			return True
	except Exception as e:
		return False


