# Copyright (C) 2015 Jeffrey Meyers
# This program is released under the "MIT License".
# Please see the file COPYING in the source
# distribution of this software for license terms.


from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine

app = Flask(__name__)
app.config.from_object('config')
app.debug = True

engine_odk = create_engine(app.config['ODK_DB_CONFIG'])
engine_onoff = create_engine(app.config['ONOFF_DB_CONFIG'])


SessionODK = scoped_session(sessionmaker(bind=engine_odk))
SessionONOFF = scoped_session(sessionmaker(bind=engine_onoff))

# make debug and error logging easier
debug = app.logger.debug
error = app.logger.error

from dashboard.mod_onoff.views import mod_onoff as onoff_module
from dashboard.mod_long.views import mod_long as long_module

app.register_blueprint(onoff_module)
app.register_blueprint(long_module)

Bootstrap(app)

from dashboard import views


