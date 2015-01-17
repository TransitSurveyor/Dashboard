from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

# modifed to False if deploying with wsgi
app.debug = True

engine = create_engine(app.config['WEB_DB_CONFIG'])
Session = scoped_session(sessionmaker(bind=engine))

# assign new function names
# to make debug and error logging easier
debug = app.logger.debug
error = app.logger.error

#from dashboard.mod_api.views import mod_api as api_module
from dashboard.mod_onoff.views import mod_onoff as onoff_module
#from dashboard.mod_long.views import mod_long as long_module

#app.register_blueprint(api_module)
app.register_blueprint(onoff_module)
#app.register_blueprint(long_module)

Bootstrap(app)

from dashboard import views


