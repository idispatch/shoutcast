# This code is licensed under the new-BSD license
# (http://www.opensource.org/licenses/bsd-license.php)
# Copyright (C) 2009 Mario Boikov <mario@beblue.org>.

import xml.etree.ElementTree as etree
import urllib
import urllib2

class ShoutCast(object):
    """
    Python front-end to the shoutcast web-radio service.
    
    This class uses urllib2.urlopen() when accessing the shoutcast service.
    Any errors that might occur while accessing the service will be propagated
    to the caller without any modifications.
    
    The shoutcast service uses XML as protocol and to parse the result from
    the service the ElementTree XML API is used. Any errors that might occur
    while parsing the XML will be propagated to the caller without any
    modifications. 
    """

    def __init__(self):
        """ Creates a Shoutcast API instance """

        self.genre_url = 'http://api.shoutcast.com/legacy/genrelist?k=ar1-ZhP_dWvHcZgq'
        self.station_url = 'http://api.shoutcast.com/legacy/genresearch?&k=ar1-ZhP_dWvHcZgq'
        self.tune_in_url = 'http://yp.shoutcast.com/sbin/tunein-station.pls?id={0}&k=ar1-ZhP_dWvHcZgq'
        self.search_url = 'http://api.shoutcast.com/legacy/stationsearch?k=ar1-ZhP_dWvHcZgq&search='
        self.nowplaying_url = 'http://api.shoutcast.com/station/nowplaying?&k=ar1-ZhP_dWvHcZgq&ct=' 
#                           http://api.shoutcast.com/legacy/stationsearch?k=[Your Dev ID]&search=ambient+beats
#        self.search_url = 'http://yp.shoutcast.com/sbin/newxml.phtml?{0}&k=ar1-ZhP_dWvHcZgq'
#        http://api.shoutcast.com/legacy/genresearch?k=[Your Dev ID]&genre=classic

    def genres(self):
        """
        Return a tuple with genres.
        Each entry in the tuple is a string with the name of the genre.
        
        Example:
        ('Rock', 'Pop', '...')
        """
        genrelist = self._parse_xml(self.genre_url)
        return tuple(genre.get('name')
                     for genre in genrelist.findall('genre') if genre.get('name'))

    def stations(self, genre):
        """
        Return a tuple with stations for the specified genre.
        Each entry in the tuple is a tulpe with the following content:
        station name, station id, bitrate, currently playing track and
        listener count

        Example:
        (('Hit Radio Station #1', 1234, 128, 'An artist - A Hit song', 123),
         ('Hit Radio Station #2', 5678, 256, 'A track name', 43)) 
        """
#
        print genre

        url = self.station_url.format(genre)
        print url
        print url+'&genre='+genre
        url=url+'&genre='+genre
        return self._generate_stations(url)

    def search(self, criteria, limit=-1):
        """ 
        Searches station name, current playing track and genre.
        To limit the result specify 'limit' to the number of items to return.
        
        Returns the same kind of tuple as stations()
        """
        params = {'search' : criteria}
        if limit > 0:
            params['limit'] = limit

        url = self.search_url # get shoutcast api search by keyword url...
        url=url+criteria       # append user entered search criteria...and pass it on :-)

        return self._generate_stations(url)
    
    #TODO : nowplaying does not work as expected.. any ideas are most welcome :-)   
        
    def nowplaying(self, criteria, limit=-1):
        """ 
        Searches station name, current playing track and genre.
        To limit the result specify 'limit' to the number of items to return.
        
        Returns the same kind of tuple as stations()
        """
        params = {'search' : criteria}
        if limit > 0:
            params['limit'] = limit

        url = self.nowplaying_url # get shoutcast api search by keyword url...
        url=url+criteria+'&f=xml'       # append user entered search criteria...and pass it on :-)
        print url
        return self._generate_stations(url)        

    def random(self):
        """ Return a tuple (same as stations()) with 20 random stations. """

        return self.stations('random')

    def top_500(self):
        """ Return a tuple (same as stations()) with the top 500 stations. """
        return self.stations('Top500')

    def tune_in(self, station_id):
        """ Return the station's play list (shoutcast pls) as a file-like object. """
        url = self.tune_in_url.format(station_id)
        return urllib2.urlopen(url)

    def _parse_xml(self, url):
        """
        Returns an ElementTree element by downloading and parsing the XML from the
        specified URL.
        """
        file = urllib2.urlopen(url)
        return etree.parse(file)

    def _generate_stations(self, url):
        """ Return a tuple with stations traversing the stationlist element tree. """
        #url='http://api.shoutcast.com/legacy/genresearch?k=ar1-ZhP_dWvHcZgq&genre=80s'  
        stationlist = self._parse_xml(url)
        result = []
#<station name=" -=Sputnik Radio Muzika=- Hi Def Sound..WARNING: Subliminal Suggestions in audio.... Server FULL? Do" mt="audio/aacp" id="639026" br="128" genre="Trance Dance Pop" ct="Gabriel &amp; Dresden - Sydney (Organised nature)" lc="45"></station>

        for station in stationlist.findall('station'):
            entry = (station.get('name'),
                     station.get('mt'),
                     station.get('id'),
                     station.get('br'),
                     station.get('genre'),
                     station.get('ct'),
                     station.get('lc'))
            result.append(entry)

        return tuple(result)
