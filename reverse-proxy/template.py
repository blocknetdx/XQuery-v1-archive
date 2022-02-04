import os
import json
import yaml
from jinja2 import Environment, FileSystemLoader, Template
from utils import concat_abis, load_json_file, load_yaml_file, write_yaml_file, write_json_file, write_text_file

J2_ENV = Environment(loader=FileSystemLoader(''), trim_blocks=True)
wd = os.getcwd()

def yaml_from_abi():
	try:
		data = concat_abis(None,None,"list")
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
		write_yaml_file(yamldata,"schema.yaml")
		return yamldata
	except Exception as e:
		print(e)

def process_template(data):
	custom_template = J2_ENV.get_template('templates/template.j2')
	rendered_data = custom_template.render(data)
	with open('/etc/nginx/nginx.conf', "w") as fname:
		fname.write(rendered_data)

def gen_data_for_template(abis):
	final_data = {}
	final_data['chains'] = []
	env = os.environ.__dict__['_data']
	entries = list(env)
	d = []
	hasura_port = ''
	hasura_ip = ''
	chain_endpoint = ''
	for e in entries:
		e = e.decode('utf-8')
		if 'CHAIN_ENDPOINT' in e:
			chain_endpoint = env[str.encode(e)].decode('utf-8')
		elif 'CHAIN_HASURA_PORT' in e:
			hasura_port = env[str.encode(e)].decode('utf-8')
		elif 'CHAIN_HASURA' in e:
			hasura_ip = env[str.encode(e)].decode('utf-8')
	final_data['port'] = os.environ.get('PORT', '80')
	final_data['endpoint'] = chain_endpoint
	final_data['hasura_ip'] = hasura_ip
	final_data['hasura_port'] = hasura_port
	final_data['chains'] = []
	for key, item in abis.items():
		for k, i in item.items():
			final_data['chains'].append({
				"name":key,
				"event":k
				})
	return final_data

def general_schema_text(data):
	text = ""
	for t in data[0]['classes'][0]['attributes']:
		text += f"  {t['name']}: {t['value'].split('(')[-1].split(',')[0].split(')')[0].capitalize()}!\n"
	final_text = """
type xquery {{
{text}
}}
""".format(text=text)
	write_text_file(final_text, "examples/schema.txt")
	print(final_text)
	
def help_text(query, data):
	port = os.environ.get('PORT', '80')
	endpoint = query['endpoint']
	text = "Powered by\n\thttps://blocknet.co\n\thttps://xquery.io\n\n"
	text +="Current Graph\n\t"+ f"http://localhost:{port}/help/graph\n\n"
	text +="List available endpoints\n\t"+ f"http://localhost:{port}/help\n\n"
	text +="GraphQL endpoint\n\t"+ f"http://localhost:{port}{endpoint}/\n\n"
	text +="GraphQL data types\n\t"+ f"http://localhost:{port}/help/schema\n\n"
	write_text_file(text, f"examples/help.txt")
	data = dict(query)
	for key, item in data.items():
		if key == 'chains':
			for i in item:
				if 'rpc_host' in list(i):
					del i['rpc_host']


	write_json_file(data, f"examples/graph.json")
	print(text)

if __name__ == "__main__":
	#gen schema
	_type = os.environ.get('SCHEMA','abi')
	wd = os.getcwd()
	data = yaml_from_abi()
	query_file = os.environ.get('QUERY_CONFIG','query.yaml')
	query = load_yaml_file(query_file)

	#load needed data
	#events with inputs
	abis_list = concat_abis(None, None, 'list')
	abis_dict = concat_abis(query, data, 'dict')
	help_text(query, abis_list)
	general_schema_text(data)

	#write nginx from jinja2 template
	final_data = gen_data_for_template(abis_dict)
	process_template(final_data)

	