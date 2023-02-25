"""Main file to run the app"""

from sys import exit
from flask_migrate import Migrate
from decouple import config

from apps.config import config_dict
from apps import create_app, db

# Don't run the app with debug set to True in productions
DEBUG = config('DEBUG', default=True, cast=bool)

# the configurations
get_config_mode = 'Debug' if DEBUG else 'Production'

try:
    # load the configurations using the default value
    app_config = config_dict[get_config_mode.capitalize()]

except KeyError:
    exit('error: Invalid <config_mode>. Expected values [Debug, Production]')

app = create_app(app_config)
Migrate(app, db)

if DEBUG:
    app.logger.info('Debug       = ' + str(DEBUG))
    app.logger.info('Environment = ' + get_config_mode)
    app.logger.info('DBMS        = ' + app_config.SQLALCHEMY_DATABASE_URI)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='5000')
