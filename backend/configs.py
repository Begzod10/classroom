import os
from dotenv import load_dotenv

load_dotenv()
api = '/api'

gennis_server_url = os.getenv('GENNIS_SERVER_URL')

turon_server_url = "http://26.196.249.247:8000"
# turon_server_url = os.getenv('TURON_SERVER_URL')
