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

""" Parser for getting Trackpoints from Runkeeper GPX data """

from xml.dom import minidom
import time
from math import pi, sin, cos, tan, atan, sqrt, asin, atan2

# http://www.movable-type.co.uk/scripts/latlong-vincenty.html
EARTH_MAJOR_AXIS = 6378388
EARTH_MINOR_AXIS = 6356911.946

DISTANCE = {'m' : 1, 'meter' : 1, 'km' : 1000, 'miles' : 1609.344,
            'mile': 1609.344}
TIMES = {'s' : 1, 'sec': 1, 'min': 60, 'hour': 3600, 'day' : 86400}

PREF_DUNIT = 'km' # set this to 'miles' if you're in the US


class Trackpoint:
    """ Class representing a single track point """
    def __init__(self, latitude=0, longitude=0, timestamp=0, elevation=0):
        self.latitude = latitude
        self.longitude = longitude
        self.timestamp = timestamp
        self.elevation = elevation
    def __str__(self):
        return "(%s,%s) elev %s on %s" % (self.latitude, self.longitude,
                                          self.elevation, self.time_str())
    def time_tuple(self):
        """ Return time tuple for the Trackpoint's timestamp """
        return time.localtime(self.timestamp)
    def time_str(self):
        """ Return string for the Trackpoint's timestamp """
        return time.ctime(self.timestamp)
    def time_to(self, trackpoint, unit='sec'):
        """ Calculated the time between this trackpoint and another one """
        return abs(self.timestamp - trackpoint.timestamp) / TIMES[unit]
    def speed_to(self, trackpoint, dunit=PREF_DUNIT, tunit='hour', pause=0,
                 skipped=0):
        """ Calculate speed between this trackpoint and another, in
            dunit/tunit. The time period used for the calculation is the
            difference between the timestamps, reduced by pause (in seconds)
            The distance used for the calculation is the distance between the
            trackpoints, reduced by skipped (in meters).
        """
        time_diff = self.time_to(trackpoint) - pause
        dist_diff = self.distance_to(trackpoint) - skipped
        try:
            return (TIMES[tunit] * dist_diff ) / (DISTANCE[dunit] * time_diff)
        except ZeroDivisionError:
            return 0.0
    def pace_to(self, trackpoint, dunit=PREF_DUNIT, tunit='min', pause=0,
                skipped=0):
        """ Calculate pace between this trackpoint and another, in
            tunit/dunit. The time period used for the calculation is the
            difference between the timestamps, reduced by pause (in seconds).
            The distance used for the calculation is the distance between the
            trackpoints, reduced by skipped (in meters).
        """
        time_diff = self.time_to(trackpoint) - pause
        dist_diff = self.distance_to(trackpoint) - skipped
        try:
            return (DISTANCE[dunit] * time_diff) / (TIMES[tunit] * dist_diff )
        except ZeroDivisionError:
            return 0.0
    def distance_to(self, trackpoint, use_elevation=True, unit='meter'):
        """ Calculate the distance to another trackpoint """
        # adapted from
        # http://www.mathworks.com/matlabcentral/fileexchange/5379
        a = EARTH_MAJOR_AXIS
        b = EARTH_MINOR_AXIS
        # convert coordinates to radians
        lat1 = self.latitude * 0.0174532925199433
        lon1 = self.longitude * 0.0174532925199433
        lat2 = trackpoint.latitude * 0.0174532925199433
        lon2 = trackpoint.longitude * 0.0174532925199433
        sign = lambda a: int(a>0) - int(a<0)
        # correct for errors at exact poles by adjusting 0.6 millimeters:
        if abs( pi / 2 - abs(lat1) ) < 1e-10:
            lat1 = sign(lat1) * ( pi / 2.0 - 1e-10 )
        if abs( pi / 2.0 - abs(lat2) ) < 1e-10:
            lat2 = sign(lat2) * ( pi / 2.0 -1e-10 )
        f = (a-b)/a
        U1 = atan((1-f) * tan(lat1))
        U2 = atan((1-f) * tan(lat2))
        lon1 = lon1 % (2 * pi)
        lon2 = lon2 % (2 * pi)
        L = abs(lon2-lon1)
        if L > pi:
            L = 2*pi - L
        lambda_v = L
        lambdaold = 0
        itercount = 0
        while True:
            itercount = itercount + 1
            if itercount > 50:
                # Points are essentially antipodal. Precision may be reduced
                # slightly.
                lambda_v = pi
                break
            lambdaold = lambda_v
            sinsigma = sqrt(   (cos(U2)*sin(lambda_v))**2
                             + (cos(U1)*sin(U2)
                                - sin(U1)*cos(U2)*cos(lambda_v))**2 )
            cossigma = sin(U1)*sin(U2) + cos(U1)*cos(U2)*cos(lambda_v)
            sigma = atan2(sinsigma, cossigma)
            try:
                alpha = asin( cos(U1)*cos(U2)*sin(lambda_v) / sin(sigma) )
            except ZeroDivisionError:
                alpha = 0.0
            cos2sigmam = cos(sigma) - 2*sin(U1)*sin(U2) / cos(alpha)**2
            C = f/16 * cos(alpha)**2 * (4 + f * (4-3*cos(alpha)**2))
            lambda_v = L + (1-C) * f * sin(alpha) * ( sigma+C*sin(sigma) \
                       * (cos2sigmam+C*cos(sigma)*(-1+2*cos2sigmam**2)) )
            # correct for convergence failure in the case of essentially
            # antipodal points
            if lambda_v > pi:
                # Points are essentially antipodal. Precision may be reduced
                # slightly.
                lambda_v = pi
                break
            if abs(lambda_v-lambdaold) > 1e-12:
                break
        u2 = cos(alpha)**2 * (a**2-b**2) / b**2
        A = 1 + u2/16384 * ( 4096 + u2*(-768 + u2*(320-175*u2)) )
        B = u2 / 1024 * ( 256 + u2*(-128 + u2*(74-47*u2)) )
        deltasigma = B * sin(sigma) * ( \
                     cos2sigmam+B/4*(cos(sigma) *(-1+2*cos2sigmam**2) \
                     - B/6 * cos2sigmam * (-3 + 4*sin(sigma)**2) \
                       * (-3+4*cos2sigmam**2))  )
        if use_elevation:
            height_diff = self.elevation - trackpoint.elevation
            return sqrt( (b * A * (sigma-deltasigma))**2
                         + height_diff**2 ) / DISTANCE[unit]
        else:
            return b * A * (sigma-deltasigma) / DISTANCE[unit]


class GPX_Error(ValueError):
    """ Error raised if there's something wrong iwth the GPX Data """
    pass


class GPX_Parser:
    """ Class for parsing a gpx file """
    def __init__(self, filename):
        self.xmldoc = minidom.parse(filename)
        self._done = False
        try:
            self.xmldoc = self.xmldoc.firstChild
            if self.xmldoc.nodeName != 'gpx':
                raise GPX_Error("root node is not 'gpx'")
        except IndexError:
            raise GPX_Error("XML file does not contain a root node")
        for child in self.xmldoc.childNodes:
            if child.nodeName == 'trk':
                self._curnode = child
                break
        for child in self._curnode.childNodes:
            if child.nodeName == 'trkseg':
                self._curnode = child
                break
    def __iter__(self):
        return self
    def number_of_segments(self):
        """ Return number of segments that are still available to be iterated
            over
        """
        curnode = self._curnode
        while curnode.nodeName != 'trkseg':
            curnode = curnode.parentNode
        result = 0
        while curnode is not None:
            if curnode.nodeName == 'trkseg':
                result = result + 1
            curnode = curnode.nextSibling
        return result
    def next(self):
        """ Return the next trackpoint """
        if self._done:
            raise StopIteration
        if self._curnode.nodeName == 'trkpt':
            next_node = self._curnode.nextSibling
            while next_node.nodeName != 'trkpt':
                next_node = next_node.nextSibling
                if next_node is None:
                    next_node = self._curnode.parentNode
                    if (next_node.nodeName != 'trkseg'):
                        raise GPX_Error("Expected to trkseg node")
                    # go to beginning of next segment
                    next_node = next_node.nextSibling
                    while next_node.nodeName != 'trkseg':
                        next_node = next_node.nextSibling
                        if next_node is None:
                            self._done = True
                            raise StopIteration # eof
                    self._curnode = next_node
                    raise StopIteration # end of segment
            self._curnode = next_node
            return self._process_trkpt()
        elif self._curnode.nodeName == 'trkseg':
            next_node = self._curnode.firstChild
            while next_node.nodeName != 'trkpt':
                next_node = next_node.nextSibling
                if next_node is None:
                    raise StopIteration # eof
            self._curnode = next_node
            return self._process_trkpt()
        else:
            raise GPX_Error("Unexpected status")
    def _process_trkpt(self):
        """ Return a Trackpoint instance generated from self._curnode, which
            must be a trkpt node
        """
        result = Trackpoint(latitude=float(self._curnode.getAttribute('lat')),
                            longitude=float(self._curnode.getAttribute('lon')))
        for trkpt_data in self._curnode.childNodes:
            if trkpt_data.nodeName == 'ele':
                elevation = ''
                for text_data in trkpt_data.childNodes:
                    if text_data.nodeType == text_data.TEXT_NODE:
                        elevation = elevation + text_data.nodeValue
                result.elevation = float(elevation)
            if trkpt_data.nodeName == 'time':
                time_string = ''
                for text_data in trkpt_data.childNodes:
                    if text_data.nodeType == text_data.TEXT_NODE:
                        time_string = time_string + text_data.nodeValue
                time_string = time_string.strip()
                result.timestamp = time.mktime(time.strptime(time_string,
                                   "%Y-%m-%dT%H:%M:%SZ"))
        return result
