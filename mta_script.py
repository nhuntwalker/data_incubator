import pandas as pd
import pandasql as sql
import numpy as np

data_df = pd.read_csv("realtime.csv").rename(columns={'Unnamed: 0': "entry_id"})

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
## Get direciton_id from trips_df
## Get trip_id from trips_df and stop_times_df
trips_df = pd.read_csv("gtfs_nyct_bus_20150103/trips.txt")
stops_df = pd.read_csv("gtfs_nyct_bus_20150103/stops.txt")
stop_times_df = pd.read_csv("gtfs_nyct_bus_20150103/stop_times.txt")

the_query = "SELECT *"
the_query += " FROM trips_df"
the_query += " WHERE route_id = 'M116'"

m116_trips = sql.sqldf(the_query, locals())


