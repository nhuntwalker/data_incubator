import pandas as pd
import pandasql as sql
import numpy as np

data_df = pd.read_csv("realtime.csv").rename(columns={'Unnamed: 0': "entry_id"})
data_df.timestamp = pd.to_datetime(data_df.timestamp, unit="s")
data_df["bus_route"] = data_df.trip_id.map(lambda x: x.split("_")[-2])

# median number of trips made by single vehicle
the_query = "SELECT vehicle_id, COUNT(DISTINCT(trip_id)) AS trip_count"
the_query += " FROM data_df"
the_query += " GROUP BY vehicle_id"

vehicle_trip_count = sql.sqldf(the_query, locals())
print np.median(vehicle_trip_count.trip_count)

# the highest total number of trips made by a Manhattan bus route
the_query = "SELECT bus_route, COUNT(DISTINCT trip_id) AS trip_count"
the_query += " FROM data_df"
the_query += " WHERE bus_route LIKE 'M%'"
the_query += " AND bus_route NOT LIKE 'MISC%'"
the_query += " GROUP BY bus_route"

manhattan_trips_count = sql.sqldf(the_query, locals())
print manhattan_trips_count[manhattan_trips_count.trip_count == max(manhattan_trips_count.trip_count)]

# What is the second-highest average speed - in Miles Per Hour - across all bus 
# routes in Manhattan?
meters_per_mile = 1609.34
the_query = "SELECT trip_id, bus_route, MAX(timestamp) AS max_time, "
the_query += "MIN(timestamp) AS min_time, "
the_query += "MAX(dist_along_route) / %s AS miles_travelled" % meters_per_mile
the_query += " FROM data_df"
the_query += " WHERE bus_route LIKE 'M%' AND bus_route NOT LIKE 'MISC%'"
the_query += " GROUP BY trip_id"
manhattan_dist_time = sql.sqldf(the_query, locals())

manhattan_dist_time.max_time = pd.to_datetime(manhattan_dist_time.max_time, unit="s")
manhattan_dist_time.min_time = pd.to_datetime(manhattan_dist_time.min_time, unit="s")
manhattan_dist_time['time_diff'] = (manhattan_dist_time.max_time - manhattan_dist_time.min_time) / np.timedelta64(1, "s") / 3600
manhattan_dist_time['avg_speed'] = manhattan_dist_time.miles_travelled / manhattan_dist_time.time_diff

the_query = "SELECT bus_route, SUM(avg_speed)/COUNT(avg_speed)"
the_query += " FROM manhattan_dist_time"
the_query += " GROUP BY bus_route"
the_query += " ORDER BY 2 DESC"
manhattan_avg_speeds = sql.sqldf(the_query, locals())
print manhattan_avg_speeds.iloc[1]

# Compute the variance of all reported headways across all stations (excluding 
# the initial station, where buses often idle) on the M116's S/W direction. 
# Give your answer in minutes^2.
## South/West-bound is toward upper west side
## direction_id = 1
## Get direction_id from trips_df
## Get trip_id from trips_df and stop_times_df
trips_df = pd.read_csv("gtfs_nyct_bus_20150103/trips.txt")
stop_times_df = pd.read_csv("gtfs_nyct_bus_20150103/stop_times.txt")

the_query = "SELECT stop_times_df.trip_id,"
the_query += " stop_times_df.arrival_time,"
the_query += " stop_times_df.departure_time,"
the_query += " stop_times_df.stop_id,"
the_query += " stop_times_df.stop_sequence,"
the_query += " trips_df.route_id"
the_query += " FROM stop_times_df JOIN trips_df"
the_query += " ON stop_times_df.trip_id = trips_df.trip_id"
the_query += " WHERE trips_df.route_id = 'M116' AND trips_df.direction_id = 1"
the_query += " AND trips_df.trip_id LIKE '%Weekday%'"
the_query += " AND trips_df.trip_id LIKE '%M116%'"
the_query += " ORDER BY 2"

m116_southbound = sql.sqldf(the_query, locals())

reformat_arrivals = m116_southbound.arrival_time
for ii in range(len(reformat_arrivals)):
    if reformat_arrivals[ii].startswith("24"):
        dum = reformat_arrivals[ii].split(":")
        dum[0] = "2015-01-29 00"
        reformat_arrivals[ii] = ":".join(dum)
    elif reformat_arrivals[ii].startswith("25"):
        dum = reformat_arrivals[ii].split(":")
        dum[0] = "2015-01-29 01"
        reformat_arrivals[ii] = ":".join(dum)
    else:
       reformat_arrivals[ii] = "2015-01-28 " + reformat_arrivals[ii]
 
m116_southbound.arrival_time = pd.to_datetime(reformat_arrivals, unit="s")
stop_list = list(set(m116_southbound[m116_southbound.stop_sequence > 1].stop_id))
arrival_differences = np.zeros(len(stop_list), dtype=list)

for ii in range(len(stop_list)):
    all_arrivals = np.sort(list(set(m116_southbound[m116_southbound.stop_id == stop_list[ii]].arrival_time)))
    time_diffs = np.zeros(len(all_arrivals)-1)
    for jj in range(len(all_arrivals)-1):
        time_diffs[jj] = (all_arrivals[jj+1] - all_arrivals[jj]) / np.timedelta64(1, "s") / 60.
    arrival_differences[ii] = time_diffs

arrival_differences = np.concatenate(arrival_differences)
var_diff = np.var(arrival_differences)

# Compute the variance of the "lateness" of bus departures (ie scheduled 
# departure time - actual departure time, note we could have "negative 
# lateness") from the initial station at 120th street and Pleasant Ave for the 
# M116 bus route in the South/West (S/W) direction. Give your answer in
# minutes^2.
stops_df = pd.read_csv("gtfs_nyct_bus_20150103/stops.txt")
reformat_departures = m116_southbound.departure_time
for ii in range(len(reformat_departures)):
    if reformat_departures[ii].startswith("24"):
        dum = reformat_departures[ii].split(":")
        dum[0] = "2015-01-29 00"
        reformat_departures[ii] = ":".join(dum)
    elif reformat_departures[ii].startswith("25"):
        dum = reformat_departures[ii].split(":")
        dum[0] = "2015-01-29 01"
        reformat_departures[ii] = ":".join(dum)
    else:
       reformat_departures[ii] = "2015-01-28 " + reformat_departures[ii]
 
m116_southbound.departure_time = pd.to_datetime(reformat_departures, unit="s")
m116_stop1 = m116_southbound[m116_southbound.stop_id == 401998] 
stop2 = int(m116_southbound[m116_southbound.stop_sequence == 2].stop_id.iloc[0])

the_query = "SELECT *"
the_query += " FROM data_df"
the_query += " WHERE bus_route LIKE 'M116' AND next_stop_id = %i" % stop2
m116_realtime_stop1 = sql.sqldf(the_query, locals())

the_query = "SELECT trip_id, MIN(timestamp) AS time, dist_from_stop"
the_query += " FROM m116_realtime_stop1 GROUP BY trip_id"
m116_realtime_stop1_times = sql.sqldf(the_query, locals())
## need to compare when they actually reported departing to when they were
## supposed to report departing
the_query = "SELECT realtime.trip_id,"
the_query += " scheduled.departure_time AS scheduled_time,"
the_query += " realtime.time AS actual_time"
the_query += " FROM m116_realtime_stop1_times AS realtime"
the_query += " JOIN m116_stop1 AS scheduled"
the_query += " ON realtime.trip_id = scheduled.trip_id"
time_diffs = sql.sqldf(the_query, locals())
delta_times = (pd.to_datetime(time_diffs.scheduled_time, unit="s") - pd.to_datetime(time_diffs.actual_time, unit="s")) / np.timedelta64(1, "m")
var_diff_stop1 = np.var(delta_times)

# You might notice that on trips, sometimes stops go unreported (or a trip is 
# not completed). Over all trips reported in the realtime data, compute the 
# percentage of scheduled stops that were not reported as an upcoming stop.
## For every trip, get every scheduled stop along that trip, not including the
##  first stop in the sequence
trips_stops_dict = {}
for trip in stop_times_df.trip_id:
    trips_stops_dict[trip] = list(stop_times_df[stop_times_df.trip_id == trip].stop_id.iloc[1:])

## For every trip in realtime get every stop along that realtime trip
trips_realtime_dict = {}
for trip in data_df.trip_id:
    all_reported_stops = list(data_df[data_df.trip_id == trip].next_stop_id.iloc)
    unique_ordered_stops = []
    for stop in all_reported_stops:
        if stop not in unique_ordered_stops:
            unique_ordered_stops.append(stop)
    trips_realtime_dict[trip] = unique_ordered_stops

## If stop not reported in sequence, unreported_count += 1
unreported_count = 0
all_reported_count = 0
for trip in trips_stops_dict:
    if trip in trips_realtime_dict.keys():
        for stop in trips_stops_dict[trip]:
            all_reported_count += 1
            if stop not in trips_realtime_dict[trip]:
                unreported_count += 1

pct = unreported_count / float(all_reported_count)