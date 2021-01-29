##Create all the imports
import numpy as np 

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt 
from dateutil.relativedelta import relativedelta

##################################################
#  Database Setup
##################################################
engine = create_engine("sqlite:///./Resources/hawaii.sqlite")

#Reflect existing database into the model
Base = automap_base()

#Reflect the tables
Base.prepare(engine, reflect=True)

#Save information reference for the tables
Measurement = Base.classes.measurement
Station = Base.classes.station
#print(Base.classes.keys())

###################################################
# Flask Setup
###################################################

app = Flask(__name__)

###################################################
# Flask Routes
###################################################

@app.route("/")
def welcome():
    """List all the available API routes."""
    return(
        f"Aloha! Welcome to the Hawaii Climate App API<br>"
        f"Mahalo for using us today!<br/>"
        f"Here are the available routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Query the database to obtain the latest 12 months of precipitation data and return results."""
    #Create the session (link) from Python to the database.
    session = Session(engine)

    #Calculate the year ago date from the last data point in the database.
    last_data_point = session.query(Measurement.date).order_by(Measurement.date.desc()).first
    (latest_date, ) = last_data_point
    latest_date = dt.datetime.strptime(latest_date, '%Y-%m-%d')
    latest_date = latest_date.date()
    year_ago = latest_date -relativedelta(years=1)
    
    #Peform a query to retrieve the data and precipitation scores
    yag_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago).all()

    session.close()

    ## Create a dictionary based on the results and use the date as a key and prcp as value.
    total_precipitation = []
    for date, prcp in yag_data:
        if prcp !=None:
            precip_dict ={}
            precip_dict[date] = prcp
            total_precipitation.append(precip_dict)
    return jsonify(total_precipitation) 

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    #Create the session (link) from Python to the database.
    session = Session(engine)

    #Query the stations
    stations = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()

    Session.close()

    #Create dictionary
    total_stations = []
    for station, name, latitude, longitude, elevation in stations:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        station_dict["latitude"] = latitude
        station_dict["longitude"] = longitude
        station_dict["elevation"] = elevation
        total_stations.append(station_dict)
    return jsonify(total_stations)
    

@app.route("/api/v1.0/tobs")
def tobs():
    """Query the database to obtain the dates and temp observations for 1 year from last data point for most active station."""
    #Create the session (link) from Python to the database.
    session = Session(engine)

    #Calculate the year ago date from the last data point in the database.
    temp_obs = session.query(Measurement.date).order_by(Measurement_date.desc()).first
    (latest_date, ) = temp_obs
    latest_date = dt.datetime.strptime(latest_date, '%Y-%m-%d')
    latest_date = latest_date.date()
    year_ago = latest_date - relativedelta(years = 1)

    #Find the most active station
    most_active = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count().desc()).first() 

    #Identify the station id of the most active station
    (most_active_id, ) = most_active
    print(f"The station id of the most active station is {most_active_id}.")

    #Peform a query to retrieve the data and precipitation scores
    yag_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active_id).filter(Measurement.date >= year_ago).all()

    session.close()

    ## Create a dictionary based on the results and use the date as a key and temp as value.
    total_temps = []
    for date, temp in yag_data:
        if temp !=None:
            temp_dict ={}
            temp_dict[date] = temp
            total_temps.append(temp_dict)
    return jsonify(total_temps) 

@app.route('/api/v1.0/<start>', defaults={'end': None})
@app.route("/api/v1.0/<start>/<end>")
def date_temps_for_date_range(start, end):
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range."""
    """When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date."""
    """When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive."""
    # Create our session (link) from Python to the DB.
    session = Session(engine)

    # For both a start date and an end date.
    if end != None:
        temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).filter(
            Measurement.date <= end).all()
    # If there is only have a start date.
    else:
        temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).all()

    session.close()

    # Convert the results to a list.
    temp_list = []
    no_temp_data = False
    for min_temp, avg_temp, max_temp in temp_data:
        if min_temp == None or avg_temp == None or max_temp == None:
            no_temp_data = True
        temp_list.append(min_temp)
        temp_list.append(avg_temp)
        temp_list.append(max_temp)
    # Return the JSON representation of dictionary.
    if no_temp_data == True:
        return f"No temperature data found for the given date range. Try another date range."
    else:
        return jsonify(temp_list)


if __name__ == '__main__':
    app.run(debug=True)










