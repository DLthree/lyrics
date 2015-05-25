import logging
import socket
import sys
import time

from suds.client import Client

logging.basicConfig(level=logging.INFO)
# logging.getLogger('suds.client').setLevel(logging.DEBUG)

class ChartLyrics(Client):
    '''
    AddLyric(xs:int trackId, xs:string trackCheckSum, xs:string lyric, xs:string email, )
    GetLyric(xs:int lyricId, xs:string lyricCheckSum, )
    SearchLyric(xs:string artist, xs:string song, )
    SearchLyricDirect(xs:string artist, xs:string song, )
    SearchLyricText(xs:string lyricText, )
    '''
    
    def __init__(self,
                 url='http://api.chartlyrics.com/apiv1.asmx?WSDL',
                 timeout=20,
                 retries=5):
        self.timeout = timeout
        self.retries = retries
        super(ChartLyrics, self).__init__(url)
        time.sleep(self.timeout)

    def retry(self, fn):
        i = 0
        while True:
            try:
                i += 1
                result = fn()
                time.sleep(self.timeout)
                return result
            except socket.error:
                logging.warn("Failed: %d of %d" % (i, self.retries))
                if i >= self.retries:
                    raise
                else:
                    time.sleep(self.timeout)
            except:
                return None
                    
    def search(self, artist, song):
        return self.retry(lambda: self.service.SearchLyricDirect(
            artist=artist, song=song))
        
client = ChartLyrics()
results = []
for line in open(sys.argv[1], 'r'):
    try:
        line = line.strip()
        print >>sys.stderr, line 
        result = client.search('Backstreet Boys', line)
        if result is None:
            continue
        print result.LyricSong
        print result.LyricArtist
        print
        print result.Lyric
        print "="*80
    except:
        pass
    

