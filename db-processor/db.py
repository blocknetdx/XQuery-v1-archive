import os
from pony.orm import *


db = Database(provider='postgres',
              host=os.environ['DB_HOST'],
              port=os.environ['DB_PORT'],
              user=os.environ['DB_USERNAME'],
              password=os.environ['DB_PASSWORD'],
              database=os.environ['DB_DATABASE'])
