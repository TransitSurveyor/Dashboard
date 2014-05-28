from web_app import app
from web_app import db
from web_app import models
from geoalchemy2.elements import WKTElement
from geoalchemy2 import functions as func

import ast

def getGroups():
    geojson = {'type': 'FeatureCollection','features': []}

    results = db.session.query(func.ST_AsGeoJSON(func.ST_Transform(models.Groups.geom,4326),10)
        .label('geom'), models.Groups.rte, models.Groups.dir)

    for result in results:
        geom = ast.literal_eval(str(result.geom))
        geojson['features'].append(geom)
 
    return geojson 

def getRoute(rte):
    results = db.session.query(func.ST_AsGeoJSON(func.ST_Transform(models.Routes.geom,4326),10)
        .label('geom'))\
        .filter_by(rte=rte)\
        .first()

    if results:
        geom = ast.literal_eval(str(results.geom))
        return geom
    else:
        return False

def getCounts():
    results = db.session.query(models.Stops.grouping).join(models.OnOffScans).join(models.Stops).group_by(models.Stops.grouping).all()
    return results