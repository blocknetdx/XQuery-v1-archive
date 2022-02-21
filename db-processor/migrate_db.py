import psycopg2 as db
import os
import yaml

host=os.environ['DB_HOST']
user=os.environ['DB_USERNAME']
password=os.environ['DB_PASSWORD']
database=os.environ['DB_DATABASE']


def load_schema():
	xquery_path = os.getcwd()+'/'+os.environ.get('schema','schema.yaml')
	with open(xquery_path) as file:
		xquery_data = yaml.load(file, Loader=yaml.FullLoader)
		order = []
		for i in xquery_data[0]['classes']:
			for j in i['attributes']:
				if j['name'] != 'id':
					order.append([j['name'],j['value']])
	return order

def get_columns(table):
	try:
		conn = db.connect(host=host, database=database, user=user, password=password)
		conn.autocommit = True
		cursor = conn.cursor()
		cursor.execute(f'select * from {table} LIMIT 0')
		colnames = [desc[0] for desc in cursor.description]
		conn.close()
		print(f'GET COLUMNS {table}')
		return colnames
	except Exception as e:
		print(f'GET COLUMNS {table}\n{e}')

def create_table(table):
	try:
		conn = db.connect(host=host, database=database, user=user, password=password)
		conn.autocommit = True
		cursor = conn.cursor()
		cursor.execute(f'CREATE TABLE {table} (id serial PRIMARY KEY)')
		conn.close()
		print(f'TABLE CREATED {table}')
	except Exception as e:
		print(f'TABLE CREATED {table}\n{e}')


def rename_column(table, old_name, new_name):
	try:
		conn = db.connect(host=host, database=database, user=user, password=password)
		conn.autocommit = True
		cursor = conn.cursor()
		cursor.execute(f'ALTER TABLE {table} RENAME COLUMN {old_name} TO {new_name}')
		conn.close()
		print(f'RENAMED {table} - {old_name} to {new_name}')
	except Exception as e:
		print(f'RENAME {table} {old_name} {new_name}\n{e}')

def not_required_column(table, name):
	try:
		conn = db.connect(host=host, database=database, user=user, password=password)
		conn.autocommit = True
		cursor = conn.cursor()
		cursor.execute(f'ALTER TABLE {table} ALTER COLUMN {name} DROP NOT NULL')
		conn.close()
		print(f'NOT_REQUIRED {table} - {name}')
	except Exception as e:
		print(f'NOT_REQUIRED {table} {name}\n{e}')

def numeric_precision(table, name):
	try:
		conn = db.connect(host=host, database=database, user=user, password=password)
		conn.autocommit = True
		cursor = conn.cursor()
		cursor.execute(f'ALTER TABLE {table} ALTER {name} SET DATA TYPE DECIMAL(1000)')
		conn.close()
		print(f'DECIMAL PRECISION {table} - {name}')
	except Exception as e:
		print(f'DECIMAL PRECISION {table} {name}\n{e}')

def set_required_column(table, name):
	try:
		conn = db.connect(host=host, database=database, user=user, password=password)
		conn.autocommit = True
		cursor = conn.cursor()
		cursor.execute(f'ALTER TABLE {table} ALTER COLUMN {name} SET NOT NULL')
		conn.close()
		print(f'SET_REQUIRED {table} - {name}')
	except Exception as e:
		print(f'SET_REQUIRED {table} {name}\n{e}')

def add_column(table, name, data_type):
	try:
		conn = db.connect(host=host, database=database, user=user, password=password)
		conn.autocommit = True
		cursor = conn.cursor()
		cursor.execute(f'ALTER TABLE {table} ADD COLUMN {name} {data_type}')
		conn.close()
		print(f'ADD {table} - {name} {data_type}')
	except Exception as e:
		print(f'ADD {table} {name} {data_type}\n{e}')

def del_column(table, name):
	try:
		conn = db.connect(host=host, database=database, user=user, password=password)
		conn.autocommit = True
		cursor = conn.cursor()
		cursor.execute(f'ALTER TABLE {table} DROP COLUMN {name}')
		conn.close()
		print(f'DEL {table} - {name}')
	except Exception as e:
		print(f'DEL {table} {name}\n{e}')


if __name__ == '__main__':
	table_name = 'xquery'
	schema = load_schema()
	create_table(table_name)

	columns = get_columns(table_name)
	for col in columns:
		if col !='id':
			not_required_column(table_name, col)

	for entry in schema:
		data_type = entry[1].split('(')[1].split(')')[0].strip()
		not_required = True if entry[1].split('(')[0].strip()=='Optional' else False
		column_name = entry[0].strip()
		if 'str' in data_type.lower():
			data_type = 'text'
		elif 'decimal' in data_type.lower():
			data_type = 'DECIMAL'
		elif 'bool' in data_type.lower():
			data_type = 'boolean'	
		add_column(table_name, column_name, data_type)
		if data_type == 'DECIMAL':
			numeric_precision(table_name, column_name)
		if not_required:
			not_required_column(table_name, column_name)
		else:
			set_required_column(table_name, column_name)
	del_column(table_name, '_data')
