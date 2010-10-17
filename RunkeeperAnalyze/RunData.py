# -*- coding: utf-8 -*-
############################################################################
#    Copyright (C) 2010 by Michael Goerz                                   #
#    http://michaelgoerz.net                                               #
#                                                                          #
#    This program is free software; you can redistribute it and/or modify  #
#    it under the terms of the GNU General Public License as published by  #
#    the Free Software Foundation; either version 3 of the License, or     #
#    (at your option) any later version.                                   #
#                                                                          #
#    This program is distributed in the hope that it will be useful,       #
#    but WITHOut ANY WARRANTY; without even the implied warranty of        #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#    GNU General Public License for more details.                          #
#                                                                          #
#    You should have received a copy of the GNU General Public License     #
#    along with this program; if not, write to the                         #
#    Free Software Foundation, Inc.,                                       #
#    59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             #
############################################################################

""" Classes containing Run Data """

from RunkeeperAnalyze.GPX_Parser import GPX_Parser, PREF_DUNIT

WALKING_SPEED = 1.8 # [m/s] running if faster, walking if slower
PAUSE_TIME = 60 # secs of walking indicating a break (new segment)

class Segment:
    """ Class that represents on Run segment """
    def __init__(self):
        self.trackpoints = []
    def total_distance(self, unit='meter'):
        """ Return the total distance covered in the segment
        """
        result = 0
        for i in xrange(1, len(self.trackpoints)):
            result = result + self.trackpoints[i].distance_to(
                              self.trackpoints[i-1], unit=unit)
        return result
    def total_time(self, unit='sec'):
        """ Return the total time the segment took """
        return self.trackpoints[0].time_to(self.trackpoints[-1], unit=unit)
    def average_speed(self, dunit=PREF_DUNIT, tunit='hour'):
        """ Return the average speed over the segment """
        return self.total_distance(unit=dunit) / self.total_time(unit=tunit)
    def average_pace(self, tunit='min', dunit=PREF_DUNIT):
        """ Return the average speed over the segment """
        return  self.total_time(unit=tunit) / self.total_distance(unit=dunit)


class Run:
    """ Class that represents a Run
    """
    def __init__(self, filename=None):
        """ Create a Run from a gpx file"""
        self.filename = filename
        self.segments = []
        self._parser = None
        if filename is not None:
            self._parser = GPX_Parser(filename)
            for seg in xrange(self._parser.number_of_segments()):
                self.segments.append(Segment())
                for trackpoint in self._parser:
                    self.segments[seg].trackpoints.append(trackpoint)
    def pause_time(self, unit='sec'):
        """ Return the total number of seconds not spent running (i.e. time
            spent between segments)
        """
        result = 0
        for i in xrange(1, len(self.segments)):
            result = result + self.segments[i].trackpoints[0].time_to(
                     self.segments[i-1].trackpoints[-1], unit=unit)
        return result
    def skipped_distance(self, unit='meter'):
        """ Return the total distance not spent running (i.e.  distance skipped
            between segments)
        """
        result = 0
        for i in xrange(1, len(self.segments)):
            result = result + self.segments[i].trackpoints[0].distance_to(
                     self.segments[i-1].trackpoints[-1], unit=unit)
        return result
    def total_distance(self, unit='meter'):
        """ Return the total distance covered in the run, including inactive
            periods
        """
        return self.active_distance(unit=unit) \
               + self.skipped_distance(unit=unit)
    def total_time(self, unit='sec'):
        """ Return the total time the run took """
        return self.segments[0].trackpoints[0].time_to(
               self.segments[-1].trackpoints[-1], unit=unit)
    def active_distance(self, unit='meter'):
        """ Return the total distance covered in the run """
        result = 0
        for segment in self.segments:
            result = result + segment.total_distance(unit=unit)
        return result
    def active_time(self, unit='second'):
        """ Return the total distance covered in the run """
        return self.total_time(unit=unit) - self.pause_time(unit=unit)
    def average_speed(self, dunit=PREF_DUNIT, tunit='hour'):
        """ Return the average speed over active periods """
        return self.active_distance(unit=dunit) / self.active_time(unit=tunit)
    def average_pace(self, tunit='min', dunit=PREF_DUNIT):
        """ Return the average speed over active periods """
        return  self.active_time(unit=tunit) / self.active_distance(unit=dunit)
    def segmentize(self):
        """ Create segments based on heuristics """
        segments = self.segments
        self.segments = []
        for segment in segments:
            self.segments += segmentize(segment)


def segmentize(segment, walking_speed=WALKING_SPEED, pause_time=PAUSE_TIME):
    """ Split on segment into several, return array of segments """
    result = [Segment(),]
    marked_trackpoint = segment.trackpoints[0]
    result[-1].trackpoints.append(marked_trackpoint)
    in_segment = True
    tp_buffer = [] # buffer for trackpoints we're undecided about
    for i in xrange(1, len(segment.trackpoints)):
        if (segment.trackpoints[i].speed_to(segment.trackpoints[i-1],
        dunit='meter', tunit='sec') > walking_speed):
            marked_trackpoint = segment.trackpoints[i]
            in_segment = True
            result[-1].trackpoints += tp_buffer
            tp_buffer = []
            result[-1].trackpoints.append(marked_trackpoint)
        else: # we're walking ...
            if (marked_trackpoint.time_to(segment.trackpoints[i])
            > pause_time):
                # ... for longer than is acceptable
                tp_buffer = []
                if in_segment:
                    result.append(Segment())
                    in_segment = False
            else:
                tp_buffer.append(segment.trackpoints[i])
    return result


