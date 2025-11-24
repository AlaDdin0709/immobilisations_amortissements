import os

SECRET_KEY = os.environ.get('SUPERSET_SECRET_KEY')

# Basic superset config
ROW_LIMIT = 5000
SUPERSET_WEBSERVER_PORT = int(os.environ.get('SUPERSET_WEBSERVER_PORT', '8088'))
