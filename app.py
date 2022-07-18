# Import dependencies
import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Set up database
engine = create_engine('sqlite:///Resources/hawaii.sqlite')

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# set up flask
app = Flask(__name__)

# Define routes
@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate API!<br/>"
        f"<br/>"
        f"<br/>"
        f"Available Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"/api/v1.0/start_date<br/>"
        f"insert start_date in yyyy-mm-dd format, the data is available up to 2017-08-23 <br/>"
        f"<br/>"
        f"/api/v1.0/start_date/end_date<br/>"
        f"insert start_date and end_date in yyyy-mm-dd format, the data is available up to 2017-08-23"
    )

@app.route("/api/v1.0/precipitation")
def precipitation_data():
    one_year_ago_date = dt.date(2017, 8 , 23) - dt.timedelta(days=365)
    session = Session(engine)
    result1 = session.query(Measurement.date , Measurement.prcp).filter(Measurement.date >= one_year_ago_date).all()
    session.close()
    
    prcp_data = []
    for date, prcp in result1:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        prcp_data.append(prcp_dict)
    return jsonify(prcp_data)
    
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    result2 = session.query(Measurement.station , Station.name).\
        filter(Measurement.station == Station.station).group_by(Measurement.station).all()

    session.close()
    
    stations_list = list(np.ravel(result2))
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    one_year_ago_date2 = dt.date(2017, 8 , 18) - dt.timedelta(days=365)
    session = Session(engine)
    result3 = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == "USC00519281").\
        filter(Measurement.date >= one_year_ago_date2).all()
    session.close()
    
    tobs_data = []
    for date, tobs in result3:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_data.append(tobs_dict)
    return jsonify(tobs_data)
    
@app.route("/api/v1.0/<start>")
def calc_temps_start(start):
    
    session = Session(engine)
    
    result4 = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= func.strftime("%Y-%m-%d",start)).all()
    
    session.close()
    
    result4_list = list(np.ravel(result4))
    
    last_date = '2017-08-23'
    
    if start <= last_date:
        return jsonify(result4_list) 
    return jsonify({"error": f"date {start} is not found. Insert start_date in yyyy-mm-dd format. The data is available up to {last_date}"}), 404

@app.route("/api/v1.0/<start>/<end>")
def calc_temps_start_end(start, end):
    
    session = Session(engine)
    
    result5 = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= func.strftime("%Y-%m-%d",start)).\
            filter(func.strftime("%Y-%m-%d", Measurement.date) <= func.strftime("%Y-%m-%d",end)).all()
    
    session.close()
    
    result5_list = list(np.ravel(result5))
    
    last_date = '2017-08-23'
    
    if start <= last_date and end <= last_date:
        return jsonify(result5_list) 
    return jsonify({"error": f"start_date or end_date is not found. Insert date in yyyy-mm-dd format. The data is available up to {last_date}"}), 404
    
if __name__ == "__main__":
    app.run(debug=True)
