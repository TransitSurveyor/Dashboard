# Copyright (C) 2015 Jeffrey Meyers
# This program is released under the "MIT License".
# Please see the file COPYING in the source
# distribution of this software for license terms.


import os, sys, json
from decimal import Decimal

from flask import Blueprint, redirect, url_for,render_template, jsonify, request
from sqlalchemy import func
from sqlalchemy.orm import aliased
from geoalchemy2 import functions as geofunc

from dashboard import SessionODK as Session
from dashboard import debug, error
from ..shared.models import Stops, SurveysCore, CallbackFlag as CFlag
from ..shared.helper import Helper
from auth import Auth

import fields as F

STATIC_DIR = '/long'
mod_long = Blueprint('long', __name__, url_prefix='/long')

def static(html, static=STATIC_DIR):
    """returns correct path to static directory"""
    return os.path.join(static, html)

@mod_long.route('/')
def index():
    return render_template(static('index.html'))

"""
def query_locations(uri):
    ret_val = {}
    On = aliased(Stops)
    Off = aliased(Stops)
    session = Session()
    record = session.query(
        SurveysCore.uri,
        func.ST_AsGeoJSON(func.ST_Transform(SurveysCore.orig_geom, 4326))
            .label('orig_geom'),
        func.ST_AsGeoJSON(func.ST_Transform(SurveysCore.dest_geom, 4326))
            .label('dest_geom'),
        func.ST_AsGeoJSON(func.ST_Transform(On.geom, 4326))
            .label('on_geom'),
        func.ST_AsGeoJSON(func.ST_Transform(Off.geom, 4326))
            .label('off_geom'))\
        .join(On, SurveysCore.board).join(Off, SurveysCore.alight)\
        .filter(SurveysCore.uri == uri).first()
    if record:
        ret_val["orig_geom"] = json.loads(record.orig_geom)
        ret_val["dest_geom"] = json.loads(record.dest_geom)
        ret_val["on_geom"] = json.loads(record.on_geom)
        ret_val["off_geom"] = json.loads(record.off_geom)
    return ret_val
 

def check_flags(record):
    if not record.flags.english:
        return False
    if not record.flags.locations:
        return False
    return True
"""

"""
Filter by route and direction
Show each tad centroid as pie chart with pct complete
"""
@mod_long.route('/map')
def map():
    session = Session()
    keys = []
    query = session.query(SurveysCore)
    for record in query:
        #TODO check that survey has not already been flagged by user
        debug(record.uri)
        #if record.flags.locations:
        keys.append(record.uri)
    session.close()
    return render_template(static('map.html'), keys=keys)


@mod_long.route('/_geoquery', methods=['GET'])
def geo_query():
    points,lines = None, None
    debug(request.args)
    if 'uri' in request.args:
        uri = request.args.get('uri')
        data = query_locations(uri)
        debug(data)
    return jsonify({'data':data})
    #return jsonify({'points':points, 'lines':lines})



@mod_long.route('/callback')
@Auth.requires_auth
def callback():
    callbacks = []
    headers = [
        "Save", "Status", "Date", "Time", "Route", "Direction",
        "Name", "Number", "Call Time", "Spanish", "Comment"]
    session = Session()
    fields = session.execute("""
        SELECT ordinal_position, column_name
        FROM information_schema.columns
        WHERE table_schema = 'web' AND table_name   = 'calls'
        ORDER BY ordinal_position;""")
    fields = [ f[1] for f in fields ]
    query = session.execute("SELECT * FROM web.calls;")
    for record in query:
        data = {}
        for index, field in enumerate(fields):
            data[field] = record[index]
        callbacks.append(data) 
    session.close()
    return render_template(
        static('callback.html'),
        headers=headers,
        callbacks=callbacks)

def convert_val(i, val):
    if i in [11, 17] and val:
        val = F.LOC_TYPE[val]
    elif i == 13 and val:
        val = F.ACCESS[val]
    elif i == 20 and val:
        val = F.EGRESS[val]
    elif i == 35 and val:
        val = val.strftime("%I:%M %p")
    elif i == 36 and val:
        val = F.STCAR_FARE[val]
    elif i == 38 and val:
        val = F.CHURN[val]
    elif i == 40 and val:
        val = F.REASON[val]
    elif i == 45 and val:
        val = F.RACE[val]
    elif i == 47 and val:
        val = F.INCOME[val]
    elif i == 50 and val:
        val = F.ENGL_PROF[val]
    if not val and val != 0: val = ''
    return val

@mod_long.route('/viewer')
def viewer():
    error("test")
    Auth.check_auth("blah", "pw")
    data = []
    headers = [
        "Save", "Option", "Date", "Time", "User", "Route", "Direction"
    ]
    session = Session()
    query = session.query(
        SurveysCore.uri,
        SurveysCore.srv_date,
        SurveysCore.start_time,
        SurveysCore.user_id,
        SurveysCore.rte,
        SurveysCore.dir
    ).order_by(SurveysCore.srv_date, SurveysCore.start_time)\
    .filter(SurveysCore.call_number == None)\
    .limit(5)
    
    callbacks = []
    for record in query:
        #debug(record)
        time = None
        if record.start_time: time = record.start_time.strftime("%I:%M %p")
        callbacks.append({
            "uri":record.uri,
            "date":record.srv_date,
            "time":time,
            "user":record.user_id,
            "rte":record.rte,
            "dir":record.dir
        })
    session.close()
    return render_template(
        static('viewer.html'),
        headers=headers,
        callbacks=callbacks)

@mod_long.route('/_survey', methods=['GET'])
def survey_data():
    data = []
    if 'uri' in request.args:
        uri = request.args.get('uri')
        session = Session()
        fields = session.execute("""
            SELECT ordinal_position, column_name
            FROM information_schema.columns
            WHERE table_schema = 'web' AND table_name   = 'callback'
            ORDER BY ordinal_position;""")
        survey = session.execute("""
            SELECT * FROM web.callback
            WHERE uri = :uri;""", {"uri":uri}).first()
        lng = session.execute("""
            SELECT choice FROM odk.lng
            WHERE survey_uri = :uri;""", {"uri":uri})
        
        if survey:
            fields = [ f[1] for f in fields ]
            for index, field in enumerate(fields):
                value = convert_val(index, survey[index])
                data.append({"field":field, "value":value})
            lngsData = {"field":"other_lngs", "value":""}
            lngs = []
            if lng:
                for record in lng:
                    if record[0]: lngs.append(F.LNG[record[0]])
            lngsData["value"] = ", ".join(lngs)
            data.insert(-2, lngsData)
        session.close()
    return jsonify({'data':data})


@mod_long.route('/_update_callback', methods=['POST'])
def update_callback():
    response = {}
    if 'uri' in request.form and 'flag' in request.form:
        uri = request.form['uri']
        flag = request.form['flag']
        debug(uri)
        debug(flag)
        session = Session()
        session.query(CFlag).filter_by(uri = uri).update({"flag":flag})
        session.commit()
        session.close()
    return jsonify(res=response)


@mod_long.route('/status')
def status():
    # TODO return routes list dynamically
    session = Session()
    routes = session.execute("""
        SELECT rte::varchar, rte_desc
        FROM web.rtedesc_lookup
        ORDER BY rte::integer""")

    routes = [ (route[0],route[1]) for route in routes ]
    status = session.execute("""
        SELECT * 
        FROM web.summary_status""")
    summary = []
    for s in status:
        summary.append({
            'bucket':str(s[0]),
            'in_target':int(s[2]),
            'in_complete':int(s[3]) if s[3] else 0,
            'in_pct':float(s[4]) if s[4] else 0,
            'out_target':int(s[5]),
            'out_complete':int(s[6]) if s[6] else 0,
            'out_pct':float(s[7]) if s[7] else 0
        })
    session.close()
    return render_template(static('status.html'), routes=routes, summary=summary)

@mod_long.route('/status/_data', methods=['GET'])
def status_data():
    data = {}
    if 'rte_desc' not in request.args: return jsonify({'data':data})
    rte_desc = request.args.get('rte_desc')
    session = Session()
    routes = session.execute("""
        SELECT
            rte,
            rte_desc,
            in_dir,
            in_dir_desc,
            out_dir,
            out_dir_desc
        FROM
            web.rtedesc_lookup
        WHERE rte_desc = :rte_desc""", {'rte_desc':rte_desc}).first()
    if not routes: return jsonify({'data':data})
    data = {
        'rte':routes[0],
        'in_dir':routes[3],
        'out_dir':routes[5],
        'status':[]
    }
    status = session.execute("""
        SELECT *
        FROM web.rte_status
        WHERE rte = :rte
        ORDER BY bucket""", {'rte':routes[0]})
    for s in status:
        data['status'].append({
            'bucket':str(s[1]),
            'in_target':int(s[2]),
            'in_complete':int(s[3]) if s[3] else 0,
            'in_pct':float(s[4]) if s[4] else 0,
            'out_target':int(s[5]),
            'out_complete':int(s[6]) if s[6] else 0,
            'out_pct':float(s[7]) if s[7] else 0
        })
    session.close()
    return jsonify({'data':data})


"""
    rtes = []
    geom = db.session.query(
        func.ST_AsGeoJSON(func.ST_Transform(func.ST_Union(Routes.geom), 4326))
        .label('geom')).filter(Routes.rte == before_rte[0]).first()
    for g in geom:
        rtes.append(json.loads(g.geom))
"""







