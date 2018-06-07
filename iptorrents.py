# VERSION: 1.00
# AUTHORS: la55u
# LICENSING INFORMATION: you do whatever the fuck you want with it

import re
import sys
import os
import logging
import tempfile

try:
    from urllib.request import Request, urlopen
except ImportError:
    from urllib2 import Request, urlopen

try:
    from urllib import urlencode, quote, unquote
    from urllib2 import URLError, HTTPError
except ImportError:
    from urllib.parse import urlencode, quote, unquote
    from urllib.error import URLError, HTTPError

debug = False
logger = logging.getLogger()
if debug:
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
else:
    from novaprinter import prettyPrinter



class iptorrents(object):
  url = 'https://iptorrents.eu'
  name = 'IPTorrents'

  ############# CHANGE THESE VALUES ONLY #################
  ### HOW TO: https://github.com/la55u/qBit-IPT-plugin ###
  cookies = {                                            #
      'uid': '1234567',                                  #
      'pass': '123very456long789randomstring012'         #
  }                                                      #
  ########################################################

  # Which search categories are supported by this search engine and their corresponding id
  # Possible categories are ('all', 'movies', 'tv', 'music', 'games', 'anime', 'software', 'pictures', 'books')
  supported_categories = {
      'all': '0',
      'movies': '72',
      'tv': '73',
      'music': '75',
      'games': '74',
      'anime': '60',
      'software': '1=&86=&95=&69=&58',
      'books': '35=&92'
  }

  def headers(self):
      return {'Cookie': ";".join(["%s=%s" % item for item in self.cookies.items()])}

  def __init__(self):
      pass

  def download_torrent(self, dl_url):
    """Downloads the torrent file into tmp directory"""

    logging.info('Attempting to download torrent')
    full_url = self.url + quote(dl_url) # for escaping spaces

    req = Request(full_url, headers=self.headers())

    file, path = tempfile.mkstemp()
    file = os.fdopen(file, "wb")
    file.write(urlopen(req).read())
    file.close()

    print(path, full_url)
    logging.info('Download complete.')

  # DO NOT CHANGE the name and parameters of this function
  # This function will be the one called by nova2.py
  def search(self, what, cat='all'):
    """Searches for what on the tracker and parses each result with regular expressions"""
    # what is a string with the search tokens, already escaped (e.g. "Ubuntu+Linux")
    # cat is the name of a search category in ('all', 'movies', 'tv', 'music', 'games', 'anime', 'software', 'pictures', 'books')

    logging.info("Searching for {}...".format(unquote(what)))

    try:
        req = Request(
            'https://iptorrents.eu/t?q=%s' % (what),
             headers=self.headers()
        )

        response = urlopen(req)
        # Only continue if response status is OK.
        if response.getcode() != 200:
            raise HTTPError(response.geturl(), response.getcode(), "HTTP request to {} failed with status: {}".format(self.url, response.getcode()), response.info(), None)
    except (URLError, HTTPError) as e:
        logging.error(e)
        raise e

    # Decoding raw html data
    data = response.read().decode()

    # one regex for extracting every data of a torrent
    regex = re.compile(r"""
        (?P<desc_link>\/details.php\?id=\d+)">                  # description link
        (?P<name>.*?)<\/a>.*?                                   # torrent title
        (?P<link>\/download.php\/\d+\/.*?\.torrent).*?          # download link
        <td.*?>(?P<size>\d+\.?\d*\s(KB|MB|GB|TB){1})<td.*?>.*?  # size
        t_seeders">(?P<seeds>\d+).*?                            # seeders count
        t_leechers">(?P<leech>\d+)                              # leechers count
        """, re.VERBOSE)                                        # ignore multiline formatting

    for match in regex.finditer(data):
        torrent = match.groupdict()
        #torrent['link'] = self.url + torrent['link']
        torrent['desc_link'] = self.url + torrent['desc_link']
        torrent['engine_url'] = self.url
        prettyPrinter(torrent)

    logging.info('Search complete.')


if __name__ == '__main__':
    ipt = iptorrents()
    #ipt.search('random')
