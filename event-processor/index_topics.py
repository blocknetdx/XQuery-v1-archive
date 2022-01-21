import os
import json
import yaml
from web3 import Web3

cwd = os.getcwd()

def load_abi():
	abi_path = os.getcwd()+'/'+os.environ.get('ABI_FILE','RC20.json')
	with open(abi_path) as file:
		abi = json.load(file)
		return abi

def get_topic(name,inputs_type):
	string = f'{name}({",".join(inputs_type)})'
	topic = Web3.keccak(text=string).hex()
	return topic



def get_combo(abi):
	name = abi['name']
	inputs = [x['type'] for x in abi['inputs']]
	return [name, inputs]


def get_dict(abi):
	d = {
	"function":[],
	"event":[]
	}
	for i in abi:
		if 'inputs' in list(i):
			if len(i['inputs'])>0 and i['type'].lower() == 'function' or i['type'].lower() == 'event':
				name, inputs = get_combo(i)
				topic = get_topic(name, inputs)
				# print(f'{name} {topic}')
				d[i['type']].append({"name":name,"topic":topic})
	for i in list(d):
		if not len(d[i]):
			del d[i]
	return d

def export_yaml(data):
	with open(f'{cwd}/index_topics.yaml', 'w+') as file:
		yaml.dump(data, file, allow_unicode=True)


if __name__ == '__main__':
	abi = load_abi()['abi']
	data = get_dict(abi)
	export_yaml(data)