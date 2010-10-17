#!/usr/bin/env python
""" Parse GPX file and show data for run described therein """

import sys
from RunkeeperAnalyze.RunData import Run

# Usage: show_run_data.py file.gpx

filename = sys.argv[-1]

def m2t(dec_min):
    """ Convert decimal minutes to min:sec """
    return "%02i:%02i" % (dec_min, (dec_min - int(dec_min)) * 60)

r = Run(filename)
r.segmentize()
accumulated_distance = 0
distance_offset = 0
for i, segment in enumerate(r.segments):
    print "Segment %s" % (i + 1)
    if (i > 0):
        distance_offset += r.segments[i].trackpoints[0].distance_to(
                                               r.segments[i-1].trackpoints[-1])
    last_tp = None
    for tp in segment.trackpoints:
        print tp
        if last_tp is not None:
            time_diff = last_tp.time_to(tp)
            dist_diff = last_tp.distance_to(tp)
            accumulated_distance += dist_diff
            print "   %s m in %s s ( %s min/km,  %s km/h)" \
                  % ( last_tp.distance_to(tp), last_tp.time_to(tp),
                      last_tp.pace_to(tp), last_tp.speed_to(tp) )
            print "   distance: %s (active), %s (abs)" % (
                               accumulated_distance / 1000,
                               (accumulated_distance + distance_offset) / 1000)
        last_tp = tp

for i, segment in enumerate(r.segments):
    print "\n** Segment %i Summary **" % (i + 1)
    print "Time (min)              : %s" % m2t(segment.total_time(unit='min'))
    print "Distance (km, miles)    : %.3f, %.3f" % (
        segment.total_distance(unit='km'), segment.total_distance(unit='miles'))
    print "Speed (km/h, mph)       : %.3f, %.3f" % (
        segment.average_speed(dunit='km'), segment.average_speed(dunit='miles'))
    print "Pace (min/km, min/mile) : %s, %s" % (
        m2t(segment.average_pace(dunit='km')),
        m2t(segment.average_pace(dunit='mile')))


print "\n**** Run Summary ****\n"
print "Total time (min)          : %s" % m2t(r.total_time(unit='min'))
print "Active time (min)         : %s" % m2t(r.active_time(unit='min'))
print "Tot. distance (km, miles) : %.3f, %.3f" % (
              r.total_distance(unit='km'), r.total_distance(unit='miles'))
print "Act. distance (km, miles) : %.3f, %.3f" % (
              r.active_distance(unit='km'), r.active_distance(unit='miles'))
print "Skip distance (km, miles) : %.3f, %.3f" % (
              r.skipped_distance(unit='km'), r.skipped_distance(unit='miles'))
print "Segments                  : %s" % len(r.segments)
print "Speed (km/h, mph)         : %.3f, %.3f" % (
             r.average_speed(dunit='km'), r.average_speed(dunit='mile'))
print "Pace (min/km, min/mile)   : %s, %s" % (
             m2t(r.average_pace(dunit='km')), m2t(r.average_pace(dunit='mile')))
