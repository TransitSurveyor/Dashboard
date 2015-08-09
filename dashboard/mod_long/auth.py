# Copyright (C) 2015 Jeffrey Meyers
# This program is released under the "MIT License".
# Please see the file COPYING in the source
# distribution of this software for license terms.


from functools import wraps
from flask import Response, request
from dashboard import app, error

class Auth(object):
    @staticmethod
    def check_auth(username, password): 
        return username == app.config["CALL_USER"] and password == app.config["CALL_PW"]

    @staticmethod
    def authenticate():
        """Sends a 401 response that enables basic auth"""
        return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})

    @staticmethod
    def requires_auth(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth = request.authorization
            if not auth or not Auth.check_auth(auth.username, auth.password):
                return Auth.authenticate()
            return f(*args, **kwargs)
        return decorated

