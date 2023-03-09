# Import Numpy
import numpy as np

# Import SQLAlchemy
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# Import Flask
from flask import Flask, jsonify

##### Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()
#Reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

##### Flask Setup
# Create an app
app = Flask(__name__)

##### Flask Routes

# Index route
@app.route("/")
def welcome():
    """List all available api routes"""
    return (
        f"Welcome to the Climate API!<br/><br/>" 
        f"All the available routs are:<br/><br/>"
        f"List of precipitation amount in inches for the time period 2016-08-23 through 2017-08-23<br/>"
        f"/api/v1.0/precipitation<br/><br/>"
        f"List of the available stations<br/>"
        f"/api/v1.0/stations<br/><br/>"
        f"List of recorded temperatures on the USC00519281 station for the time period 2016-08-18 through 2017-08-18<br/>"
        # USC00519281 station last record has been made 2017-08-18
        f"/api/v1.0/tobs<br/><br/>"
        f"When given the start date in format YYYY-MM-DD, the average, maximum and minimum temperatures for the time interval will display<br/>\
                    Available dates: 2010-01-01 through 2017-08-23<br/>\
                        *All stations data<br/>"
        f"/api/v1.0/<start><br/><br/>"
        f"When given the start and the end date in format YYYY-MM-DD, the average, maximum and minimum temperatures for the time interval will display<br/>\
                    Available dates: 2010-01-01 through 2017-08-23<br/>\
                        *All stations data<br/>"         
        f"/api/v1.0/<start>/<end><br/>"
    )


# Precipitation route 
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB 
    session = Session(engine)
    # Query precipitation table
    data_precip = [Measurement.date, Measurement.prcp]
    results = session.query(*data_precip).filter(Measurement.date >= '2016-08-23').order_by(Measurement.date).all()

    session.close()

    # Create a dictionary from the row data and append to a list of year_precip
    year_precip = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict[date] = prcp
        
        year_precip.append(prcp_dict)

    return jsonify (year_precip)

# Stations route 
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB 
    session = Session(engine)
    # Query stations table
    results = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()

    session.close()

    # Create a dictionary
    hawaii_stations = []
    for station, name, latitude, longitude, elevation in results:
        stations_dict = {}
        stations_dict[station] = name, latitude, longitude, elevation
        
        hawaii_stations.append(stations_dict)

    return jsonify (hawaii_stations)

# Tobs route 
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB 
    session = Session(engine)
    # Query tobs table
    tobs_data = [Measurement.date, Measurement.tobs]
    results = session.query(*tobs_data).filter(Measurement.station == 'USC00519281')\
        .filter(Measurement.date >= '2016-08-18').order_by(Measurement.date).all()

    session.close()

    # Create a dictionary from the row data and append to a list of year_tobs
    year_tobs = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict[date] = tobs
        
        year_tobs.append(tobs_dict)

    return jsonify (year_tobs)

# Start route 
@app.route("/api/v1.0/<start>")
def start_date(start):
    # Create our session (link) from Python to the DB 
    session = Session(engine)

    # Query average, maximum and minimum value
    results = session.query(func.avg(Measurement.tobs),\
                            func.max(Measurement.tobs),\
                            func.min(Measurement.tobs)).\
                            filter(Measurement.date >= start).all()
    
    # Query end and start date in the data set
    startdate = session.query(func.min(Measurement.date)).scalar()
    enddate = session.query(func.max(Measurement.date)).scalar()   

    session.close()
    
    # Create the list of data
    temp_list = []
    for avg_temp, max_temp, min_temp in results:
        temp_list.append(avg_temp)
        temp_list.append(max_temp)
        temp_list.append(min_temp)

        if start >= startdate and start <= enddate:
            return jsonify(temp_list)
        else: 
            return jsonify({"error": "The input data is out of range."}), 404

 # Start/end route 
@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    # Create our session (link) from Python to the DB 
    session = Session(engine)

    # Query average, maximum and minimum value
    results = session.query(func.avg(Measurement.tobs),\
                            func.max(Measurement.tobs),\
                            func.min(Measurement.tobs)).\
                            filter(Measurement.date >= start).\
                            filter(Measurement.date <= end).all()
    
    # Query end and start date in the data set
    startdate = session.query(func.min(Measurement.date)).scalar()
    enddate = session.query(func.max(Measurement.date)).scalar() 

    session.close()
    
    # Create the list of data
    temp_list = []
    for avg_temp, max_temp, min_temp in results:
        temp_list.append(avg_temp)
        temp_list.append(max_temp)
        temp_list.append(min_temp)
    
        if start >= startdate and start <= enddate and end >= startdate and end <= enddate:
            return jsonify(temp_list)
        else: 
            return jsonify({"error": "The input data is out of range."}), 404    


if __name__ == "__main__":
    app.run(debug=True)