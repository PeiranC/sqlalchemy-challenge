
# Import Dependencies
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from flask import Flask, jsonify

# Database Setup
engine = create_engine('sqlite:///Resources/hawaii.sqlite')
# Reflect existing database into a new model
Base = automap_base()
# Reflect tables
Base.prepare(engine, reflect=True)
# View all classes
Base.classes.keys()
# Save to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create link
session = Session(engine)
# Setup Flask
app = Flask(__name__)

@app.route("/")
def home():
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date 1 year ago from the last data point in the database
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    year_ago = dt.datetime.strptime(last_date, "%Y-%m-%d") - dt.timedelta(days=365)
    
    # Query the last 12 months of precipitation data
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= year_ago).all()
    
    # Convert the query results to a dictionary with date as the key and prcp as the value
    precipitation = {date: prcp for date, prcp in results}
    
    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def stations():
    # Query all stations
    results = session.query(Station.station).all()
    
    # Convert the query results to a list
    stations = list(np.ravel(results))
    
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Calculate the date 1 year ago from the last data point in the database
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    year_ago = dt.datetime.strptime(last_date, "%Y-%m-%d") - dt.timedelta(days=365)
    
    # Query the most active station in the last year of data
    station_counts = session.query(Measurement.station, func.count(Measurement.station)).\
        filter(Measurement.date >= year_ago).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).all()
    most_active_station = station_counts[0][0]
    
    # Query the last 12 months of temperature observation data for the most active station
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= year_ago).\
        filter(Measurement.station == most_active_station).all()
    
    # Convert the query results to a list