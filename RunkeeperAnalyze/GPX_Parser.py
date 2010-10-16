# -*- coding: utf-8 -*-
############################################################################
#    Copyright (C) 2008 by Michael Goerz                                   #
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

""" Parser for Runkeeper GPX data """

from xml.dom import minidom    
import time

class Trackpoint:
    """ Class representing a single track point """
    def __init__(self, latitude=0, longitude=0, timestamp=0, elevation=0):
        self.latitude = latitude
        self.longitude = longitude
        self.timestamp = timestamp
        self.elevation = elevation
    def __str__(self):
        return "(%s,%s) elev %s at %s" % (self.latitude, self.longitude, 
                                          self.elevation, self.timestamp)
    def distance_to(self, trackpoint):
        """ Calculate the distance (in m) to another trackpoint """
        pass


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
        result = Trackpoint(latitude=self._curnode.getAttribute('lat'),
                            longitude=self._curnode.getAttribute('lon'))
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
