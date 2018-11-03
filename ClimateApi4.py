from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt
from dateutil.relativedelta import relativedelta
from dateutil import parser as ps
# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func,inspect,text
from flask import Flask, jsonify,request



#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# We can view all of the classes that automap found
Base.classes.keys()
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(bind=engine)
"""Return a list off dates and prcp"""
# Latest Date
last=session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
#12 Months Ago
oneyerago=ps.parse(last).date()-relativedelta(months=+12)
oneyerago=str(oneyerago)
      
# Query Prcp
results =session.query(Measurement.date,Measurement.prcp).filter(Measurement.date >= oneyerago).filter(Measurement.date <= last).\
    group_by(Measurement.date).\
    order_by(Measurement.date.desc()).all()
#Query Station List

stationlist=session.query(Station.id,Station.station,Station.name).all()
#Query previuous years tobs
templist =session.query(Measurement.date,Measurement.tobs).filter(Measurement.date >= oneyerago).filter(Measurement.date <= last).\
    group_by(Measurement.date).\
    order_by(Measurement.date.desc()).all()

#Query for start and end date
conn= session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))
missing = object()

    

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################


@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/prcpdata<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/dates"
        
    )


@app.route("/api/v1.0/prcpdata", methods=['GET'])
def prcpdata():
    
    prcli = []
    for Me in results:
        prcp_dict = {}
        prcp_dict["Date"] =Me.date
        prcp_dict["Prcp"] = Me.prcp
        prcli.append(prcp_dict)
    
    return jsonify(prcli)

@app.route("/api/v1.0/stations" ,methods=['GET'])
def stations():
    stationli = []
    for Stn in stationlist:
        station_dict = {}
        station_dict["Station"] =Stn.station
        station_dict["Name"] = Stn.name
        stationli.append(station_dict)
    
    return jsonify(stationli)

@app.route("/api/v1.0/tobs", methods=['GET'])
def tobs():
    
    tobsli = []
    for t in templist:
        tobs_dict = {}
        tobs_dict["Date"] =t.date
        tobs_dict["tobs"] = t.tobs
        tobsli.append(tobs_dict)
    
    return jsonify(tobsli)
@app.route("/api/v1.0/dates/<start_date>/<end_date>",methods=['GET','POST'])

def dates(start_date,end_date=missing):
    if end_date is missing:
        data=conn.filter(Measurement.date >= start_date).all()
        li=[]
        retMap = {'tmin': data[0][0],'tavg': data[0][1],'tmax': data[0][2]}
        li.append(retMap)
        return jsonify(li)
           
    else:
            data=conn.filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
            li=[]
            retMap = {'tmin': data[0][0],'tavg': data[0][1],'tmax': data[0][2]}
            li.append(retMap)
            return jsonify(li)


    
if __name__ == '__main__':
    app.run(debug=True)
