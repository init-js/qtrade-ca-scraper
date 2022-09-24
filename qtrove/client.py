from qtrove.constants import QTRADE_BASE_URL
from . import auth
from . import config
from .scrapers import accounts

class Client(object):
    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password
        self.session = None

        if None in (username, password):
            qcfg = config.get_config()
            self.username = qcfg['username']
            self.password = qcfg['password']

    def connect(self):
        """Run the Auth workflow against Qtrade."""
        self.session = auth.run_auth(self.username, self.password)
        self.password = None

    def get_accounts(self):
        accounts.load_accounts(self.session)