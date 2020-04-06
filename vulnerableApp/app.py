from flask import Flask, request
from tld import get_tld
from dns import resolve
import requests
app = Flask(__name__)

BLACKLIST = ['127.0.0.1', '0.0.0.0']

"""
This is a very ugly and half-functioning example of vulnerable code:
(I know, it probably has dozen of other ssrfs inside but for testing purposes it's just fine :D)
"""

@app.route('/')
def vuln():
    if 'url' in request.args:
        try:
            url = request.args['url']
            info = get_tld(url, as_object=True)
            if resolve(info.parsed_url[1]) not in BLACKLIST: # <- First the domain needst to resolve to non-blacklist IP
                return requests.get(url).text # <- After the check passes, it can resolve to whatever you want :D
            else:
                return 'blacklisted'
        except:
            return 'bad url'
    else:
        return 'supply url to GET `url`'
