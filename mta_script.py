import pandas as pd
import pandasql as sql
import numpy as np

data_df = pd.read_csv("realtime.csv").rename(columns={'Unnamed: 0': "entry_id"})
data_df.timestamp = pd.to_datetime(data_df.timestamp, unit="s")
# median number of trips made by single vehicle
the_query = "SELECT vehicle_id, COUNT(DISTINCT(trip_id)) AS trip_count"
the_query += " FROM data_df"
the_query += " GROUP BY vehicle_id"

vehicle_trip_count = sql.sqldf(the_query, locals())
print np.median(vehicle_trip_count.trip_count)

# the highest total number of trips made by a Manhattan bus route
data_df["bus_route"] = data_df.trip_id.map(lambda x: x.split("_")[-2])

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
# minutes^2. You can make the simplifying assumption that the first reported
# status on a SW-bound trip at the initial station is the departure time.
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
m116_realtime_stop1.timestamp = pd.to_datetime(m116_realtime_stop1.timestamp, unit = "s")
## need to compare when they actually reported departing to when they were
# supposed to report departing
the_query = "SELECT trip_id, MIN(timestamp), dist_from_stop"
the_query += " FROM m116_realtime_stop1 GROUP BY trip_id"

