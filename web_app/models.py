from flask.ext.sqlalchemy import orm
from geoalchemy2 import Geometry

from web_app import db


class OnScan(db.Model):
    #TODO make stop_id reference tm_stops
    id = db.Column(db.Integer, primary_key = True)
    uuid = db.Column(db.Text)
    date = db.Column(db.DateTime)
    line = db.Column(db.Text)
    dir = db.Column(db.Text)
    match = db.Column(db.Boolean)
    geom = db.Column(Geometry(geometry_type='POINT', srid=2913))
    stop_id = db.Column(db.Integer, db.ForeignKey("tm_stops.gid"), nullable=False)
    dist = db.Column(db.Float)
    stops = orm.relationship("Stops")

    def __init__(self, uuid, date, line, dir, geom, stop_id, dist):
        self.uuid = uuid
        self.date = date
        self.line = line
        self.dir = dir
        self.match = False
        self.geom = geom
        self.stop_id = stop_id
        self.dist = dist
    
    def __repr__(self):
        return '<OnScan: %r>' % self.id

class OffScan(db.Model):
    #TODO make stop_id reference tm_stops
    id = db.Column(db.Integer, primary_key = True)
    uuid = db.Column(db.Text)
    date = db.Column(db.DateTime)
    line = db.Column(db.Text)
    dir = db.Column(db.Text)
    match = db.Column(db.Boolean)
    geom = db.Column(Geometry(geometry_type='POINT', srid=2913))
    stop_id = db.Column(db.Integer, db.ForeignKey("tm_stops.gid"), nullable=False)
    dist = db.Column(db.Float)
    stops = orm.relationship("Stops")

    def __init__(self, uuid, date, line, dir, match, geom, stop_id, dist):
        self.uuid = uuid
        self.date = date
        self.line = line
        self.dir = dir
        self.match = match
        self.geom = geom
        self.stop_id = stop_id
        self.dist = dist

    def __repr__(self):
        return '<OffScan: %r>' % self.id

class OnOffPairs(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    line = db.Column(db.Text)
    dir = db.Column(db.Text)
    on_id = db.Column(db.Integer, db.ForeignKey("on_scan.id"), nullable=False)
    off_id = db.Column(db.Integer, db.ForeignKey("off_scan.id"), nullable=False)
    on = orm.relationship("OnScan")
    off = orm.relationship("OffScan")

    def __init__(self, line, dir, on_id, off_id):
        self.line = line
        self.dir = dir
        self.on_id = on_id
        self.off_id = off_id

    def __repr__(self):
        return '<OnOffPairs: %r>' % self.id

class Stops(db.Model):
   __tablename__ = 'tm_stops'
   gid = db.Column(db.Integer, primary_key = True)
   rte = db.Column(db.SmallInteger)
   rte_desc = db.Column(db.Text)
   dir = db.Column(db.SmallInteger)
   dir_desc = db.Column(db.Text)
   stop_name = db.Column(db.Text)
   stop_seq = db.Column(db.Integer)
   stop_id = db.Column(db.Integer)
   geom = db.Column(Geometry(geometry_type='POINT', srid=2913))
   grouping = db.Column(db.Integer)

   def __repr__(self):
       return '<Stops: %r>' % self.stop_id
   

class Routes(db.Model):
   __tablename__ = 'tm_routes'
   gid = db.Column(db.Integer, primary_key = True)
   rte = db.Column(db.SmallInteger)
   dir = db.Column(db.SmallInteger)
   rte_desc = db.Column(db.Text)
   dir_desc = db.Column(db.Text)
   geom = db.Column(Geometry(geometry_type='MULTILINESTRING', srid=2913))
   
   def __repr__(self):
       return '<Routes: %r>' % self.rte

class Groups(db.Model):
   __tablename__ = 'groups'
   id = db.Column(db.Integer, primary_key = True)
   rte = db.Column(db.SmallInteger)
   dir = db.Column(db.SmallInteger)
   grouping = db.Column(db.SmallInteger)
   geom = db.Column(Geometry(geometry_type='POINT', srid=2913))

   def __repr__(self):
       return '<uuid: %r>' % self.id


