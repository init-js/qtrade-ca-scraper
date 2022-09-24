import requests
import logging
from qtrove.utils import save_response
from qtrove.constants import QTRADE_BASE_URL

log = logging.getLogger(__name__)

def load_accounts_page(session: requests.Session):
    log.info("loading accounts page")
    basic_portfolio = session.get(QTRADE_BASE_URL + "trading/tradingDispatch.do?nav=portfolioBasicView")
    save_response(basic_portfolio)
