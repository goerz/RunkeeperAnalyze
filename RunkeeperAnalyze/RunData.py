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


from GPX_Parser import GPX_Parser

class Segment:
    """ Class that represents on Run segment """
    def __init__(self):
        self.trackpoints = []


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

    def total_distance(self):
        """ Return the total distance (in m) covered in the run """
        pass
    def total_time(self):
        """ Return the total time the run took """
        pass
    def active_meters(self):
        """ Return the total distance covered in the run """
        pass
    def active_kilometers(self):
        """ Return the total distance covered in the run """
        pass
    def active_miles(self):
        """ Return the total distance covered in the run """
        pass
    def active_time(self):
        """ Return the total time spent running """
        pass
    def average_pace(self, unit='km'):
        """ Return the average pace in seconds per unit """
        pass
    def kilometers(self):
        """ Return a tuple of Runs, one for each active kilometer """
        pass
    def miles(self):
        """ Return a tuple of Runs, one for each active mile """
        pass


