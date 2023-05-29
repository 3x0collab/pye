import os
import datetime


import csv
import json
import openpyxl
import xml.etree.ElementTree as ET

from sqlalchemy import create_engine,inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base

class Connectors(object):
	"""docstring for Connectors"""
	def __init__(self, connector=None,task=None):
		super(Connectors, self).__init__()
		self.task = task
		self.connector = connector
		self.credentials = json.loads(connector.parameters)
		self.name = connector.name
		self.connector_type = connector.connector_type
		self.data = []
		print(f"Connecting to {self.name} Connector")
		self.connect()
	
	def connect(self):
		pass

	def get(self):
		return self.data

	def post(self,data):
		self.data = data

	def log_connection(self,method="GET",data=[]):
		log(self.name+f"_{self.connector.pk}_{method}_logs",f"""Connector {method} method run succesfully, with {len(data)} records.\n""")
		



class DatasetConnector(Connectors):
	"""docstring for DatasetConnector"""
	def __init__(self,connector=None,task=None):
		super(DatasetConnector, self).__init__(connector,task) 
		

	def connect(self):
		# print('here now', self.credentials)
		for x in range(int(self.credentials['datasets_number'])):
			self.data.append(json.loads(self.credentials['datasets_content']))
		self.log_connection('GET',self.data)

	def post(self,data):
		log(self.name+"-"+str(self.connector.pk),data)
		self.log_connection('POST',data)




class FileConnector(Connectors):
	"""docstring for DatasetConnector"""
	def __init__(self,connector=None,task=None):
		super(FileConnector, self).__init__(connector,task)

	def connect(self):
		save_data = []
		for file_model in self.connector.files.all():
			file_name = file_model.file.name
			data = self.read_file(
				file_model.filetype,
				file_model.file,
				self.credentials.get("delimiter"),
				self.credentials.get("quotechar")
				)
			save_data = save_data +data
		self.data = save_data
		self.log_connection('GET',self.data)
 
		

	def read_file(self, file_type, file, delimiter=None, quotechar=None):
		file_path = file.path
		if file_type == 'csv':
			with open(file_path, 'r') as f:
				reader = csv.DictReader(f, delimiter=delimiter, quotechar=quotechar)
				data = [dict(row) for row in reader]
			return data
		elif file_type == 'excel':
			workbook = openpyxl.load_workbook(filename=file_path)
			sheet = workbook.active
			data = []
			headers = [cell.value for cell in sheet[1]]
			for row in sheet.iter_rows(min_row=2):
				row_data = {headers[i]: cell.value for i, cell in enumerate(row)}
				data.append(row_data)
			return data
		elif file_type == 'json':
			with open(file_path, 'r') as f:
				data = json.load(f)
			return data
		elif file_type == 'xml':
			tree = ET.parse(file_path)
			root = tree.getroot()
			data = []
			for child in root:
				row_data = {subchild.tag: subchild.text for subchild in child}
				data.append(row_data)
			return data
		# elif file_type == 'other':
		#	 with open(file_path, 'r') as f:
		#		 data = f.readlines()
		#	 return data
		else:
			raise ValueError(f'Unsupported file type: {file_type}') 

	def post(self,data):
		log(self.name+"-"+str(self.connector.pk),data)
		self.log_connection('POST',data)




class DatabaseConnector(Connectors):
	"""docstring for DatasetConnector"""
	def __init__(self,connector=None,task=None):
		super(DatabaseConnector, self).__init__(connector,task)

	def connect(self):
		self.connect_to_database()
		self.data = self.pull_data()
		self.log_connection('GET',self.data)



	def connect_to_database(self):

		# Extract form inputs
		db_type = self.credentials['db_type']
		host = self.credentials['host']
		port = self.credentials['port']
		db_name = self.credentials['db_name']
		username = self.credentials['username']
		password = self.credentials['password']
		sql_query = self.credentials['sql_query']

		# Database connection URL
		if db_type == 'postgresql':
			db_url = f'postgresql://{username}:{password}@{host}:{port}/{db_name}'
		elif db_type == 'mysql':
			db_url = f'mysql+pymysql://{username}:{password}@{host}:{port}/{db_name}'
		elif db_type == 'sqlite':
			db_url = f'sqlite:///{db_name}'
		elif db_type == 'oracle':
			db_url = f'oracle://{username}:{password}@{host}:{port}/{db_name}'
		elif db_type == 'mssql':
			db_url = f'mssql+pyodbc://{username}:{password}@{host}:{port}/{db_name}'

		# Connect to the database 
		self.engine = create_engine(db_url)
		Session = sessionmaker(bind=self.engine)
		self.session = Session()

	def pull_data(self):
		# Execute SQL query
		table_name = self.credentials.get('table_name',"")
		sql_query = self.credentials['sql_query']
		query_params = self.get_query_params()

		if sql_query:
			result = self.session.execute(sql_query,query_params)
		else:
			result = self.session.execute(f'SELECT * FROM {table_name}' )

		column_names = [desc[0] for desc in result.cursor.description]  # Retrieve column names from the ResultSet

		data = []
		while True:
			rows = result.fetchmany(50)  # Retrieve 50 rows at a time
			if not rows:
				break
			data.extend([dict(zip(column_names, row)) for row in rows])

		return data

	def get_primary_key(self, table_name):
		Base = declarative_base(bind=self.engine)
		Base.metadata.reflect()

		# Check if the table exists in the reflected metadata
		if table_name.lower() in Base.metadata.tables.keys():
			# Get the table object
			table = Base.metadata.tables[table_name.lower()]
			inspector = inspect(self.engine)
			primary_key_columns = inspector.get_pk_constraint(table_name)['constrained_columns']
			primary_key_column = primary_key_columns[0] if primary_key_columns else None
			# Print the primary key column name
			if primary_key_column:
				if table_name.isupper():
					return primary_key_column.upper()
			return primary_key_column
		else:
			print("Table does not exist")

	
	def get_query_params(self):
		params = {}
		params['LAST_RUN_DATE'] = str(self.task.last_run_date)
		params['LAST_RUN_TIME'] = str(self.task.last_run_time)
		return params

	def post(self,data=[]):
		table_name = self.credentials.get('table_name',"")
		pk = self.get_primary_key(table_name)
		query_params = self.get_query_params()

		# Perform data updates or inserts
		if isinstance(data, list):
			for entry in data:
				try:
					self.session.execute(f"INSERT INTO {table_name} ({', '.join(entry.keys())}) VALUES ({', '.join([f':{key}' for key in entry.keys()])})", {**entry,**query_params})
				except IntegrityError:
					update_values = ', '.join([f"{key} = :{key}" for key in entry.keys()])
					self.session.execute(f"UPDATE {table_name} SET {update_values} WHERE {pk} = :{pk}", {**entry,**query_params})
		elif isinstance(data, dict):
			for key, value in data.items():
				for entry in value:
					try:
						self.session.execute(f"INSERT INTO {table_name} ({', '.join(entry.keys())}) VALUES ({', '.join([f':{key}' for key in entry.keys()])})", {**entry,**query_params})
					except IntegrityError:
						update_values = ', '.join([f"{key} = :{key}" for key in entry.keys()])
						self.session.execute(f"UPDATE {table_name} SET {update_values} WHERE {pk} = :{pk}", {**entry,**query_params})

		# Commit the changes
		self.session.commit()
		# Close the session
		self.session.close()

		self.log_connection('POST',data)


	
class TaskConnector(Connectors):
	"""docstring for DatasetConnector"""
	def __init__(self,connector=None,task=None):
		super(TaskConnector, self).__init__(connector,task)

	def connect(self):
		pass


class APIConnector(Connectors):
	"""docstring for DatasetConnector"""
	def __init__(self,connector=None,task=None):
		super(APIConnector, self).__init__(connector,task)

	def connect(self):
		pass


class ApplicationConnector(Connectors):
	"""docstring for DatasetConnector"""
	def __init__(self,connector=None,task=None):
		super(ApplicationConnector, self).__init__(connector,task)

	def connect(self):
		pass



class SocialConnector(Connectors):
	"""docstring for DatasetConnector"""
	def __init__(self,connector=None,task=None):
		super(SocialConnector, self).__init__(connector,task)

	def connect(self):
		pass





class CloudConnector(Connectors):
	"""docstring for DatasetConnector"""
	def __init__(self,connector=None,task=None):
		super(CloudConnector, self).__init__(connector,task)

	def connect(self):
		pass





class IOTConnector(Connectors):
	"""docstring for DatasetConnector"""
	def __init__(self,connector=None,task=None):
		super(IOTConnector, self).__init__(connector,task)

	def connect(self):
		pass




connector_map = {
	"dummy":DatasetConnector,
	"task":TaskConnector,
	"database":DatabaseConnector,
	"flatfile":FileConnector,
	"api":APIConnector,
	"application":ApplicationConnector,
	"social_media":SocialConnector,
	"cloud":CloudConnector,
	"iot":IOTConnector,

}	

def pick_connector(Connector,task):
	con =  connector_map[Connector.connector_type](Connector,task) 
	return con


def log(name,data=[]):
		path = os.getcwd()
		name = name.replace(":","_")
		path = os.path.join(path,'logs',name)
		print('path',path)
		os.makedirs(path, exist_ok=True)
		date_strf = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
		log_file = os.path.join(path, f'{date_strf}.txt')
		with open(log_file, "a") as f:
			if isinstance(data, str):
				f.write(data)
			elif isinstance(data, (list, tuple,set)):
				for item in data:
					f.write(str(item) + "\n")
			elif isinstance(data, dict):
				for key, value in data.items():
					f.write(str(key) + ": " + str(value) + "\n")
			else:
				f.write(str(data))

				
# credentials = {"csrfmiddlewaretoken": "HMvy80qcSzVZpqrSANusg6k75MZQWwrIio9xFfDosyFAl69qMuPxvVVN1leoz1F4", "connector_type": "dummy", "connector_pk": "4", "datasets": "BasicNewsArticles", "datasets_content": "{\"article_id\":\"ART001\",\"headline\":\"COVID-19 Cases Continue to Rise Across the Globe\",\"article_text\":\"As the Omicron variant spreads, COVID-19 cases are surging worldwide. Health officials are urging people to get vaccinated and follow safety guidelines to help slow the spread of the virus.\",\"publish_date\":\"03/13/2023\",\"source\":\"CNN\",\"keywords\":[\"COVID-19\",\"Omicron variant\",\"health officials\",\"vaccinated\",\"safety guidelines\",\"slow the spread\"],\"entities\":[{\"entity_name\":\"COVID-19\",\"entity_type\":\"Disease\"},{\"entity_name\":\"Omicron\",\"entity_type\":\"Variant\"},{\"entity_name\":\"CNN\",\"entity_type\":\"Organization\"}]}", "datasets_number": "10"}
# dummy1 = DummyConnector(credentials)
# print(dummy1.name)
# dummy_data = dummy1.get()[0]
# print(dummy_data['article_id'])
	