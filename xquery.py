#!/usr/bin/env python3
import os
import yaml
from jinja2 import Environment, FileSystemLoader, Template
import argparse
import ipaddress
wd = os.getcwd()

def load_yaml(FILE):
	with open(FILE) as file:
		data = yaml.load(file, Loader=yaml.FullLoader)
		return data

def gen_ips(subnet,exclude):
	ips = [str(ip) for ip in ipaddress.IPv4Network(subnet)]
	return ips[2::]

def process_yaml(data,OUTPUT_FILE):
	custom_template = J2_ENV.get_template('/autobuild/docker-compose.j2')
	rendered_data = custom_template.render(data)
	with open(wd+f'/{OUTPUT_FILE}', "w") as fname:
		fname.write(rendered_data)
	print(f'Generated {wd}/{OUTPUT_FILE}')

if __name__ == "__main__":
	J2_ENV = Environment(loader=FileSystemLoader(''), trim_blocks=True)

	parser = argparse.ArgumentParser()
	parser.add_argument('--yaml',   help='yaml filename to process | query.yaml', default='query.yaml')
	parser.add_argument('--output', help='output docker-compose file name | docker-compose.yaml', default='docker-compose.yaml')
	parser.add_argument('--subnet', help='docker-compose subnet network | 172.31.0.0/24', default='172.31.0.0/24')

	args = parser.parse_args()
	QUERY_FILE = args.yaml
	OUTPUT_FILE = args.output
	SUBNET = args.subnet
	
	ips = gen_ips(SUBNET,None)
	hasura_port = 8080
	postgres_port = 5432
	gateway_port1 = 5555
	gateway_port2 = 5556
	reverse_proxy_port = 80

	query_file = load_yaml(f'{wd}/{QUERY_FILE}')
	
	final_data = {}
	final_data['chains'] = []
	for key0, item0 in query_file.items():
		if key0 == 'chains':
			for item in item0:
				name = item['name']
				for event in item['query']:
					event[f'ip'] = ips.pop(0)
				final_data['chains'].append(item)
		elif key0 == 'graph':
			final_data[key0] = item0
		elif key0 == 'endpoint':
			final_data[key0] = item0

	final_data['postgres_ip'] = ips.pop(0)
	final_data['postgres_port'] = str(postgres_port)
	final_data['gateway_processor_ip'] = ips.pop(0)
	final_data['gateway_processor_port1'] = str(gateway_port1)
	final_data['gateway_processor_port2'] = str(gateway_port2)
	final_data['db_processor_ip'] = ips.pop(0)
	final_data['graphql_engine_ip'] = ips.pop(0)
	final_data['graphql_engine_port'] = str(hasura_port)
	final_data['reverse_proxy_ip'] = ips.pop(0)
	final_data['reverse_proxy_port'] = reverse_proxy_port
	final_data['query_config'] = QUERY_FILE	
	final_data['subnet'] = SUBNET
	process_yaml(final_data,OUTPUT_FILE)
