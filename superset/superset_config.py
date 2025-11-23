import os

# Read SECRET_KEY from environment (12-factor). The container must provide this.
# Do not hardcode secrets in source.
SECRET_KEY = os.environ.get('SUPERSET_SECRET_KEY')

# Basic superset config
ROW_LIMIT = 5000
SUPERSET_WEBSERVER_PORT = int(os.environ.get('SUPERSET_WEBSERVER_PORT', '8088'))
