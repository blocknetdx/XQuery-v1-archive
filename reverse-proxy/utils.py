import os
import json 
import yaml

wd = os.getcwd()

def concat_abis(query, schema_data, _type):
	env = os.environ.__dict__['_data']
	abis = {}
	abis["RC20"] = "RC20.json"
	final_data_list = []
	final_data_dict = {"RC20":{}}
	for key, item in env.items():
		i = item.decode('utf-8')
		k = key.decode('utf-8')
		if 'CHAIN_ABI_' in k:
			name = k.split('CHAIN_ABI_')[-1]
			abis[name] = i
			if name in list(final_data_dict):
				final_data_dict[name].append(i)
			else:
				final_data_dict[name] = {}
	for abi, abi_file in abis.items():
		with open(f'{wd}/{abi_file}') as file:
			data = json.load(file)
			for a in data['abi']:
				final_data_list.append(a)
				if _type == 'dict':
					query_events = []
					for chain in query['chains']:
						if chain['name'] == abi:
							query_events = [q['name'] for q in chain['query']]
					if a['type'].lower() in ['event','function']:
						final_data_dict[abi][a['name']] = {}
						for x in a['inputs']:
							item = f'xquery_{x["name"]}'
							for y in schema_data[0]['classes'][0]['attributes']:
								if y['name'].lower() == item.lower():
									data_type = f"{y['value'].split('(')[-1].split(',')[0].split(')')[0].capitalize()}!"
									final_data_dict[abi][a['name']][item.lower()] = data_type
						if a['name'] == 'Swap':
							final_data_dict[abi][a['name']]["xquery_token1_symbol"] = 'Str!'
							final_data_dict[abi][a['name']]["xquery_token1_name"] = 'Str!'
							final_data_dict[abi][a['name']]["xquery_token1_decimals"] = 'Str!'
							final_data_dict[abi][a['name']]["xquery_token0_symbol"] = 'Str!'
							final_data_dict[abi][a['name']]["xquery_token0_name"] = 'Str!'
							final_data_dict[abi][a['name']]["xquery_token0_decimals"] = 'Str!'
							final_data_dict[abi][a['name']]["xquery_fn_name"] = 'Str!'
							final_data_dict[abi][a['name']]["xquery_blocknumber"] = 'Int!'
							final_data_dict[abi][a['name']]["xquery_timestamp"] = 'Int!'
	if _type == 'list':
		return final_data_list
	elif _type == 'dict':
		return final_data_dict

def load_json_file(filename):
	with open(f'{wd}/{filename}') as file:
		data = json.load(file)
		return data

def load_yaml_file(filename):
	with open(f'{wd}/{filename}') as file:
		data = yaml.load(file, Loader=yaml.FullLoader)
		return data

def write_json_file(data, filename):
	with open(f'{wd}/{filename}', 'w') as file:
		json.dump(data, file)
		print(f'Wrote {filename}')

def write_yaml_file(data, filename):
	with open(f'{wd}/{filename}', 'w') as file:
		yaml.dump(data, file, allow_unicode=True)
		print(f'Wrote {filename}')

def write_text_file(data, filename):
	with open(f'{wd}/{filename}', 'w') as file:
		file.write(data)
		print(f'Wrote {filename}')