from flask import render_template
from flask import redirect
from flask import request
from flask import jsonify

from geoalchemy2 import functions as func

from web_app import app
from web_app import db
import models
import query
from insert import InsertScan

import datetime

@app.route('/')
def index():
    return render_template('base.html')

@app.route('/input', methods=['POST'])
def submit():
    if request.method == 'POST':
        uuid = request.form['uuid']
        date = datetime.datetime.strptime(request.form['date'], "%Y-%m-%d %H:%M:%S")
        line = request.form['line']
        dir = request.form['dir']
        lon = request.form['lon']
        lat = request.form['lat']
        mode = request.form['mode']

        #insert data into database
        insert = InsertScan(uuid,date,line,dir,lon,lat,mode)
    
    return jsonify(success='True')


@app.route('/map')
def map():
    return render_template('map.html')


@app.route('/_getRte')
def getRte():
    rte = request.args.get('rte')
    data = query.getRoute(rte)
    return jsonify(results=data) 

@app.route('/_getGroups')
def getGrp():
    data = query.getGroups()
    return jsonify(results=data) 

@app.route('/_Test')
def getGrp():
    data = query.getCounts()
    for i in data:
        app.logger.debug(i[0].line)
    return "hello"

