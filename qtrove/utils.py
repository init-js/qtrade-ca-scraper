from ast import parse
import os, os.path
import requests
from urllib.parse import urlparse, quote
import logging

log = logging.getLogger(__name__)

def save_response(response: requests.Response, outputdir="./pages"):
    os.makedirs(outputdir, exist_ok=True)
    parsed_url =urlparse(response.url)
    safe_path = os.path.join(outputdir, quote(parsed_url.path + "?" + parsed_url.query, safe=''))
    with open(safe_path, "w+") as fd:
        fd.write(response.text)
    log.debug("wrote page %s to file %s", response.url, safe_path)

