#!/usr/bin/env python
""" Parse GPX file and show data for run described therein """

import sys
from RunkeeperAnalyze.RunData import Run

# Usage: show_run_data.py file.gpx

filename = sys.argv[-1]

r = Run(filename)
for i, segment in enumerate(r.segments):
    print "Segment %s" % (i + 1)
    last_tp = None
    for tp in segment.trackpoints:
        print tp
        if last_tp is not None:
            time_diff = last_tp.time_to(tp)
            dist_diff = last_tp.distance_to(tp)
            print "   %s m in %s s ( %s min/km,  %s km/h)" \
                  % ( last_tp.distance_to(tp), last_tp.time_to(tp), 
                      last_tp.pace_to(tp), last_tp.speed_to(tp) )
        last_tp = tp

print "\n**** Run Information ****\n"
print "Total time (min)          : %s" % r.total_time(unit='min')
print "Active time (min)         : %s" % r.active_time(unit='min')
print "Tot. distance (km, miles) : %s, %s" % (r.total_distance(unit='km'), 
                                              r.total_distance(unit='miles'))
print "Act. distance (km, miles) : %s, %s" % (r.active_distance(unit='km'), 
                                              r.active_distance(unit='miles'))
print "Segments        : %s" % len(r.segments)
print "Speed (km/h)    : %s" % r.average_speed(dunit='km')
print "Speed (mph)     : %s" % r.average_speed(dunit='miles')
print "Pace (min/km)   : %s" % r.average_pace(dunit='km')
print "Pace (min/mile) : %s" % r.average_pace(dunit='miles')
