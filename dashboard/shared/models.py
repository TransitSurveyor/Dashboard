from sqlalchemy import Column, Integer, Numeric, SmallInteger, Text, String, Boolean
from sqlalchemy import DateTime, Boolean, ForeignKey, create_engine
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2 import Geometry

import constants as cons


"""
Database Models
"""
Base = declarative_base()

class Users(Base):
    __tablename__ = "users"    
    id = Column(Integer, primary_key = True)
    first = Column(Text)
    last = Column(Text)
    username = Column(Text)
    password_hash = Column(Text)

    def __init__(self, first, last, username, password_hash):
        self.first = first
        self.last = last
        self.username = username
        self.password_hash = password_hash

    def __repr__(self):
        return '<User: Name: %r %r, Username:%r >' %\
            (self.first, self.last, self.username)



class OnTemp(Base):
    __tablename__ = 'on_temp'
    id = Column(Integer, primary_key = True)
    uuid = Column(Text)
    date = Column(DateTime)
    line = Column(Text)
    dir = Column(Text)
    match = Column(Boolean)
    geom = Column(Geometry(geometry_type='POINT', srid=2913))
    user_id = Column(Text, ForeignKey("users.username"), nullable=False)
    user = relationship("Users", foreign_keys=user_id)

    def __init__(self, uuid, date, line, dir, geom, user_id):
        self.uuid = uuid
        self.date = date
        self.line = line
        self.dir = dir
        self.match = False
        self.geom = geom
        self.user_id = user_id

    def __repr__(self):
        return '<OnTemp: %r, %r, %r, %r, %r >' %\
            (self.id, self.uuid, self.date, self.line, self.dir)

class OffTemp(Base):
    __tablename__ = 'off_temp'
    id = Column(Integer, primary_key = True)
    uuid = Column(Text)
    date = Column(DateTime)
    line = Column(Text)
    dir = Column(Text)
    match = Column(Boolean)
    geom = Column(Geometry(geometry_type='POINT', srid=2913))
    user_id = Column(Text, ForeignKey("users.username"), nullable=False)
    user = relationship("Users", foreign_keys=user_id)

    def __init__(self, uuid, date, line, dir, geom, user_id, match):
        self.uuid = uuid
        self.date = date
        self.line = line
        self.dir = dir
        self.match = match
        self.geom = geom
        self.user_id = user_id

    def __repr__(self):
        return '<OnTemp: %r, %r, %r, %r, %r >' %\
            (self.id, self.uuid, self.date, self.line, self.dir)


class Scans(Base):
    __tablename__ = 'scans'
    id = Column(Integer, primary_key = True)
    date = Column(DateTime)
    line = Column(Text)
    dir = Column(Text)
    geom = Column(Geometry(geometry_type='POINT', srid=2913))
    user_id = Column(Text)
    stop = Column(Integer, ForeignKey("tm_route_stops.gid"), nullable=False)
    stop_key = relationship("Stops", foreign_keys=stop)

    def __init__(self, **kwargs):
        self.id = kwargs[cons.ID]
        self.date = kwargs[cons.DATE]
        self.line = kwargs[cons.LINE]
        self.dir = kwargs[cons.DIR]
        self.geom = kwargs[cons.GEOM]
        self.user_id = kwargs[cons.USER_ID]
        self.stop = kwargs[cons.STOP]

    def __repr__(self):
        return '<OnTemp: %r, %r, %r, %r >' %\
            (self.id, self.date, self.line, self.dir)


class OnOffPairs_Scans(Base):
    __tablename__ = 'on_off_pairs__scans'
    id = Column(Integer, primary_key = True)
    on_id = Column(Integer, ForeignKey("scans.id"), nullable=False)
    off_id = Column(Integer, ForeignKey("scans.id"), nullable=False)
    on = relationship("Scans", foreign_keys=on_id)
    off = relationship("Scans", foreign_keys=off_id)

    def __init__(self, **kwargs):
        self.id = kwargs[cons.ID]
        self.on_id = kwargs[cons.ON_ID]
        self.off_id = kwargs[cons.OFF_ID]

    def __repr__(self):
        return '<OnOffPairs: id:%r, on_id:%r, off_id:%r >' %\
            (self.id, self.on_id, self.off_id)


class OnOffPairs_Stops(Base):
    __tablename__ = 'on_off_pairs__stops'
    id = Column(Integer, primary_key = True)
    date = Column(DateTime)
    line = Column(Text)
    dir = Column(Text)
    on_stop = Column(Integer, ForeignKey("tm_route_stops.gid"), nullable=False)
    off_stop = Column(Integer, ForeignKey("tm_route_stops.gid"), nullable=False)
    on = relationship("Stops", foreign_keys=on_stop)
    off = relationship("Stops", foreign_keys=off_stop)
    user_id = Column(Text)


    def __init__(self, **kwargs):
        self.id = kwargs[cons.ID]
        self.date = kwargs[cons.DATE]
        self.line = kwargs[cons.LINE]
        self.dir = kwargs[cons.DIR]
        self.on_stop = kwargs[cons.ON_STOP]
        self.off_stop = kwargs[cons.OFF_STOP]
        self.user_id = kwargs[cons.USER_ID]


    def __repr__(self):
        return '<OnOffPairs: id:%r, on_id:%r, off_id:%r >' %\
            (self.id, self.on_stop, self.off_stop)


class Stops(Base):
    __tablename__ = 'tm_route_stops'
    gid = Column(Integer, primary_key = True)
    rte = Column(SmallInteger)
    rte_desc = Column(Text)
    dir = Column(SmallInteger)
    dir_desc = Column(Text)
    stop_name = Column(Text)
    stop_seq = Column(Integer)
    stop_id = Column(Integer)
    geom = Column(Geometry(geometry_type='POINT', srid=2913))

    def __repr__(self):
        return '<Stops: %r %r>' % (self.stop_id, self.stop_name)

class Quotas(Base):
    __tablename__ = 'quota'
    id = Column(Integer, primary_key = True)
    rte = Column(Text)
    rte_desc = Column(Text)
    dir = Column(Text)
    dir_desc = Column(Text)
    ridership = Column(Integer)
    onoff_target = Column(Integer)
    main_target = Column(Integer)

    def __repr__(self):
        return '<Quota ID: %r>' % (self.id)


class Routes(Base):
    __tablename__ = 'tm_routes'
    gid = Column(Integer, primary_key = True)
    rte = Column(SmallInteger)
    dir = Column(SmallInteger)
    rte_desc = Column(Text)
    public_rte = Column(Text)
    dir_desc = Column(Text)
    frequent = Column(Text) 
    type = Column(Text)
    geom = Column(Geometry(geometry_type='MULTILINESTRING', srid=2913))

    def __repr__(self):
        return '<Routes: %r %r>' % (self.rte, self.rte_desc)

class StopsODK(Base):
    __tablename__ = 'stops'
    __table_args__ = {"schema":"tm"}
    gid = Column(Integer, primary_key = True)
    rte = Column(SmallInteger)
    rte_desc = Column(Text)
    dir = Column(SmallInteger)
    dir_desc = Column(Text)
    stop_name = Column(Text)
    stop_seq = Column(Integer)
    stop_id = Column(Integer)
    geom = Column(Geometry(geometry_type='POINT', srid=2913))

    def __repr__(self):
        return '<Stops: %r %r>' % (self.stop_id, self.stop_name)


class SurveysCore(Base):
    __tablename__ = 'survey' 
    __table_args__ = {"schema":"odk"}
    uri = Column(String, primary_key=True)
    
    user_id = Column(String)
    deviceid = Column(String)
    srv_date = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    
    rte = Column(Integer)
    dir = Column(Integer)
    
    english = Column(Boolean)
    other_lng = Column(Integer)
    
    orig_geom = Column(Geometry(geometry_type='POINT', srid=2913))
    orig_purpose = Column(Integer)
    orig_purpose_other = Column(String)
    orig_access = Column(Integer)
    orig_access_other = Column(String)
    orig_blocks = Column(Integer)
    orig_parking = Column(String)
    
    dest_geom = Column(Geometry(geometry_type='POINT', srid=2913))
    dest_purpose = Column(Integer)
    dest_purpose_other = Column(String)
    dest_egress = Column(Integer)
    dest_egress_other = Column(String)
    dest_blocks = Column(Integer)
    dest_parking = Column(String)
    
    board_id = Column(Integer, ForeignKey("tm.stops.gid"), nullable=True)
    alight_id = Column(Integer, ForeignKey("tm.stops.gid"), nullable=True)
    
    board = relationship("StopsODK", foreign_keys=board_id)
    alight = relationship("StopsODK", foreign_keys=alight_id)
    
    route1 = Column(String)
    route2 = Column(String)
    route3 = Column(String)
    route4 = Column(String)
    route5 = Column(String)
    
    #loc_valid = Column(String)
    
    reverse_trip = Column(Boolean)
    reverse_time = Column(DateTime)
    stcar_fare = Column(Integer)
    stcar_fare_other = Column(String)
    churn = Column(Integer)
    churn_other = Column(String)
    reason = Column(Integer)
    
    license = Column(Boolean)
    house_no = Column(Integer)
    wrk_out_house = Column(Integer)
    wrk_veh = Column(Integer)
    race = Column(Integer)
    race_other = Column(String)
    income = Column(Integer)
    addit_lng = Column(Boolean)
    engl_prof = Column(Integer)
   
    call_name = Column(String)
    call_number = Column(String)
    call_time = Column(String)
    call_spanish = Column(String)
    call_comment = Column(String)
    
    def __repr__(self):
        return '<Survey: uri:%r, rte:%r, dir:%r>' % \
            (self.uri, self.user_id, elf.rte, self.dir)

class SurveysFlag(Base):
    __tablename__ = 'flags'
    __table_args__ = {"schema":"odk"}
    uri = Column(String, primary_key=True)
    english = Column(Boolean)
    loc = Column(Boolean)
    count = Column(Integer)

class CallbackFlag(Base):
    __tablename__ = 'callback_flags'
    __table_args__ = {"schema":"odk"}
    uri = Column(String, ForeignKey("odk.survey.uri"), primary_key=True)
    flag = Column(Integer)
    parent = relationship("SurveysCore", foreign_keys=uri)

    #off_stop = Column(Integer, ForeignKey("tm_route_stops.gid"), nullable=False)
    #on = relationship("Stops", foreign_keys=on_stop)

class SurveysLng(Base):
    __tablename__ = 'lng'
    __table_args__ = {"schema":"odk"}
    uri = Column(String, primary_key = True)
    survey_uri = Column(String)
    choice = Column(Text)



