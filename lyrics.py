import sys
import logging
import urllib2
import re
import time

logging.basicConfig(level=logging.INFO)

from suds.client import Client
from xml.etree import ElementTree
    
c = Client('http://lyrics.wikia.com/server.php?wsdl')
data_dir = "data"

def get_songs(artist):
    result = c.service.getArtist(artist)
    songs = []
    for album in result.albums:
        songs.extend(album.songs)
    return songs

def get_titles(artist, songs, limit=None):
    urls = []
    for song in songs[:limit]:
        try:
            result = c.service.getSong(artist, song)
            if result.lyrics == "Not found":
                logging.warn("%s:%s not found" % (artist, song))
                continue
            urls.append(result.url)
            time.sleep(0.1) # rate limit ourselves
        except Exception as e:
            logging.error(str(e))

    titles = []
    prefix = "http://lyrics.wikia.com/"
    for url in urls:
        try:
            assert url.startswith(prefix)
            title = url[len(prefix):]
            titles.append(title)
        except Exception as e:
            logging.error(str(e))
            
    return titles

def get_content(url):
    response = urllib2.urlopen(url)
    time.sleep(0.1) # rate limit
    return response.read()


def get_lyrics(titles):
    lyrics = []
    prefix = "http://lyrics.wikia.com/api.php?action=query&prop=revisions&rvprop=content&format=xml&titles="
    for title in titles:
        try:
            logging.info(title)
            url = prefix + title
            content = get_content(url)

            et = ElementTree.fromstring(content)
            txt = et.find("query").find("pages").find("page") \
                .find("revisions").find("rev").text
            mo = re.search("<lyrics>(.*)</lyrics>", txt, re.DOTALL)
            if not mo:
                logging.warn("get_lyrics(%s) no mo" % title)
                continue
            lyrics.append(mo.group(1))
        except Exception as e:
            logging.error(str(e))
    return lyrics

def cached(artist, cache_name, fn, force_update=False):
    cache_file = os.path.join(data_dir, "%s-%s.json" % (artist, cache_name))
    if not force_update and os.path.exists(cache_file):
        with open(cache_file, "r") as f:
            result = json.load(f)
    else:
        result = fn() # call the actual function
        with open(cache_file, "w") as f:
            json.dump(result, f)
    return result
    
def main(artists):
    for artist in artists:
        cache = lambda cache_name, fn:\
                cached(artist, cache_name, fn, force_update=False)
        songs = cache("songs", lambda: get_songs(artist))
        titles = cache("titles", lambda: get_titles(artist, songs, limit=None))
        lyrics = cache("lyrics", lambda: get_lyrics(titles))
        for lyric in lyrics:
            print unicode(lyric).encode('utf-8')
    
if __name__ == "__main__":
    artists = [
        "Taylor Swift",
        "One Direction",
        "Ed Sheeran",
        "Selena Gomez",
        "Ariana Grande",
        "Jonas Brothers",
        "The Wanted",
        "Katy Perry",
        "Kelly Clarkson",
        "Backstreet Boys",
        "NSYNC",
        "New Kids on the Block",
        "Spice Girls",
        ]
    main(artists)
    # main(sys.argv[1:])
    
