import os, sys, json
from decimal import Decimal

from flask import Blueprint, redirect, url_for,render_template, jsonify, request
from sqlalchemy import func
from sqlalchemy.orm import aliased
from geoalchemy2 import functions as geofunc

from dashboard import Session, debug, error
from ..shared.models import Stops, SurveysCore
#from ..shared.models import Stops, Routes, SurveysCore, #SurveysFlag
from ..shared.helper import Helper

import fields as F

STATIC_DIR = '/long'
mod_long = Blueprint('long', __name__, url_prefix='/long')


def static(html, static=STATIC_DIR):
    """returns correct path to static directory"""
    return os.path.join(static, html)


@mod_long.route('/')
def index():
    return redirect(url_for('.map'))

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
def callback():
    data = []
    headers = [
        "Save", "Status", "Date", "Time", "Route", "Direction",
        "Name", "Number", "Call Time", "Spanish", "Comment"]
    session = Session()
    query = session.query(
        SurveysCore.uri,
        SurveysCore.srv_date,
        SurveysCore.start_time,
        SurveysCore.rte,
        SurveysCore.dir,
        SurveysCore.call_name,
        SurveysCore.call_number,
        SurveysCore.call_time,
        SurveysCore.call_spanish,
        SurveysCore.call_comment
    ).order_by(SurveysCore.srv_date, SurveysCore.start_time)\
    .filter(SurveysCore.call_number != None)

    callbacks = []
    for record in query:
        #debug(record)
        callbacks.append({
            "uri":record.uri,
            "date":record.srv_date,
            "time":record.start_time,
            "rte":record.rte,
            "dir":record.dir,
            "name":record.call_name,
            "number":record.call_number,
            "calltime":record.call_time,
            "comment":record.call_comment,
            "spanish":record.call_spanish
        })
    session.close()
    return render_template(
        static('callback.html'),
        headers=headers,
        callbacks=callbacks)

def convert_val(i, val):
    if i in [9, 15] and val:
        val = F.LOC_TYPE[val]
    elif i == 11 and val:
        val = F.ACCESS[val]
    elif i == 17 and val:
        debug(val)
        val = F.EGRESS[val]
    elif i == 31 and val:
        val = val.strftime("%I:%M %p")
        debug(type(val))
    elif i == 32 and val:
        val = F.STCAR_FARE[val]
    elif i == 34 and val:
        val = F.CHURN[val]
    elif i == 36 and val:
        val = F.REASON[val]
    elif i == 41 and val:
        val = F.RACE[val]
    elif i == 43 and val:
        val = F.INCOME[val]
    elif i == 46 and val:
        val = F.ENGL_PROF[val]
    if not val and val != 0: val = ''
    return val

@mod_long.route('/viewer')
def viewer():
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
        callbacks.append({
            "uri":record.uri,
            "date":record.srv_date,
            "time":record.start_time,
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
        fields_res = session.execute("""
            SELECT ordinal_position, column_name
            FROM information_schema.columns
            WHERE table_schema = 'web' AND table_name   = 'callback'
            ORDER BY ordinal_position;""")
        fields = [ f[1] for f in fields_res ]
        
        select = ""
        for index, field in enumerate(fields):
            if index != len(field) - 2:
                select += field + ", "
            else:
                select += field
        debug(select)
        query = session.execute("""
            SELECT * FROM web.callback
            WHERE uri = :uri;""", {"uri":uri})
        for record in query:
            for index, field in enumerate(fields):
                value = convert_val(index, record[index])
                data.append({"field":field, "value":value})
        session.close()
    return jsonify({'data':data})

"""
def transfers(query):
    before = 0
    after = 0
    before_rte = []
    after_rte = []

    
    if query and query.transfers_before and query.transfers_after:
        before = int(query.transfers_before)
        after = int(query.transfers_after)

        if before > 0:
            before_rte.append(query.tb_1)
            if before > 1:
                before_rte.append(query.tb_2)
                if before > 2:
                    before_rte.append(query.tb_3)
        
        if after > 0:
            after_rte.append(query.ta_1)
            if after > 1:
                after_rte.append(query.ta_2)
                if after > 2:
                    after_rte.append(query.ta_3)
    
    rtes = []
    print "before"
    for rte in before_rte:
        print rte
        geom = db.session.query(
            func.ST_AsGeoJSON(func.ST_Transform(func.ST_Union(Routes.geom), 4326))
            .label('geom')).filter(Routes.rte == before_rte[0]).first()
        rtes.append(json.loads(geom.geom))
        #for g in geom:
        #    rtes.append(json.loads(g.geom))
    print "after"
    for rte in after_rte:
        print rte
        geom = db.session.query(
            func.ST_AsGeoJSON(func.ST_Transform(func.ST_Union(Routes.geom), 4326))
            .label('geom')).filter(Routes.rte == before_rte[0]).first()
        rtes.append(json.loads(geom.geom))
        #for g in geom:
        #    rtes.append(json.loads(g.geom))

"""







