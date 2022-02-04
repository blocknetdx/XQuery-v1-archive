import json
import os
import yaml
from jinja2 import Environment, FileSystemLoader, Template

J2_ENV = Environment(loader=FileSystemLoader(''),trim_blocks=True)

#create data from multiple abis or single one
def concat_abis():
	wd = os.getcwd()
	env = os.environ.__dict__['_data']
	abis = ['RC20.json']
	final_data = []
	for key, item in env.items():
		i = item.decode('utf-8')
		k = key.decode('utf-8')
		if 'CHAIN_ABI_' in k:
			abis.append(i)
	for abi in abis:
		with open(f'{wd}/{abi}') as file:
			data = json.load(file)
			for a in data['abi']:
				final_data.append(a)
	return final_data

#make yaml schema from abi
def yaml_from_abi():
	try:
		data = concat_abis()
		inputs = []
		inputs.append({'name':'id','value':'PrimaryKey(int, auto=True)'})
		inputs.append({'name':'xquery_chain_name','value':'Required(str)'})
		inputs.append({'name':'xquery_query_name','value':'Required(str)'})
		inputs.append({'name':'xquery_timestamp','value':'Required(int)'})
		inputs.append({'name':'xquery_tx_hash','value':'Required(str)'})
		inputs.append({'name':'xquery_token0_name','value':'Optional(str)'})
		inputs.append({'name':'xquery_token0_symbol','value':'Optional(str)'})
		inputs.append({'name':'xquery_token0_decimals','value':'Optional(str)'})
		inputs.append({'name':'xquery_token1_name','value':'Optional(str)'})
		inputs.append({'name':'xquery_token1_symbol','value':'Optional(str)'})
		inputs.append({'name':'xquery_token1_decimals','value':'Optional(str)'})
		inputs.append({'name':'xquery_side','value':'Optional(str)'})
		inputs.append({'name':'xquery_address_filter','value':'Optional(str)'})
		inputs.append({'name':'xquery_blocknumber','value':'Optional(int)'})
		inputs.append({'name':'xquery_fn_name','value':'Optional(str)'})
		for i in data:
			if i['type'].lower() in ['event','function']:
				for k in i['inputs']:
					name = k['name']
					val = 'Optional(str)'
					if name == '':
						name = 'xquery_none'
					if '_' not in name:
						name = 'xquery_'+name
					if '_' == name[0]:
						name = 'xquery'+name
					d = {'name':name.lower(),'value':val}
					if d not in inputs:
						inputs.append(d)
		inputs = list({v['name']:v for v in inputs}.values())
		yamldata = [{"classes":[{"name":"XQuery","attributes":inputs}]}]
		with open(wd+'/schema.yaml', "w") as fname:
			yaml.dump(yamldata, fname, allow_unicode=True)
		return(yamldata)  
	except Exception as e:
		pass
		print(e)

#load yaml
def load_yaml(yamlfilename):
	try:
		with open(yamlfilename) as fname:
			datalist = yaml.load(fname, Loader=yaml.FullLoader)
	except Exception as e:
		return 'ERROR'
	return datalist

#process jinja2 template from yaml schema
def process_yaml(data):
	custom_template = J2_ENV.get_template('/templates/models.j2')
	rendered_data = custom_template.render(data)
	with open(wd+'/models.py', "w") as fname:
		fname.write(rendered_data)


if __name__ == "__main__":
	_type = os.environ.get('SCHEMA','abi')
	wd = os.getcwd()

	if _type == 'schema':
		file_name = wd+'/schema.yaml'
		data = load_yaml(file_name)
	elif _type == 'abi':
		data = yaml_from_abi()        
	if data == 'ERROR':
		print("ERROR loading YAML")
	else:
		process_yaml(data[0])