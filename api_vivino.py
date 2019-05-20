#from . import http
#from .http import client
import http.client
import json
import zlib
import re
import time
from wine import *
from random import randint


def get_session_key():
    headers = {"Host": "www.vivino.com",
               "Connection": "keep-alive",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
               "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36",
               "Accept-Encoding": "gzip, deflate, br",
               "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"}
    conn = http.client.HTTPSConnection("vivino.com", 443)
    conn.request("GET", "/contact", headers=headers)
    res = conn.getresponse()
    pattern = r'\_ruby-web_session=(\S*)\b'
    string = res.getheader(name='Set-Cookie')
    match = re.search(pattern, string)
    return match[1]


def get_wines(web_session_key, serialized_request):
    headers = {"Host": "www.vivino.com",
               "Connection": "keep-alive",
               "Accept": "application/json",
               "X-Requested-With": "XMLHttpRequest",
               "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36",
               "Content-Type": "application/json",
               "Accept-Encoding": "gzip, deflate, br",
               "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
               "Cookie": "ruby-web_session=" + web_session_key}
    conn = http.client.HTTPSConnection("vivino.com", 443)
    conn.request("GET", "/api/explore/explore" + serialized_request, headers=headers)
    res = conn.getresponse()
    decompressed_data = zlib.decompress(res.read(), 16 + zlib.MAX_WBITS)
    parsed = json.loads(decompressed_data, object_hook=as_wine)

    vintages = parsed['explore_vintage']['matches']
    wines = []
    for vintage in vintages:
        wines.append(vintage)
    return wines


#key = get_session_key()

