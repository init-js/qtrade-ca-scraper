import logging
import toml

CFG_FILE = 'qtrove.toml'

log = logging.getLogger(__name__)

def get_config():
    if not get_config._cfg:
        try:
            get_config._cfg = toml.load(CFG_FILE)
        except IOError as ioe:
            log.info("%s not found. loading defaults.", CFG_FILE)
            get_config._cfg = toml.loads("")

    return get_config._cfg

get_config._cfg = None
