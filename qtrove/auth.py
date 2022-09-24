import requests
import re
import logging

from qtrove.constants import QTRADE_BASE_URL
from .utils import save_response

log = logging.getLogger(__name__)

CSRF_RE = re.compile('<input type="hidden" name="_csrf" value="([^"]+)" />', re.DOTALL)
OTP_POST_RE = re.compile(' action="/security/qi/security-auth/verify/otp" method="post"')
NO_TRUST_URL = '/security/qi/security-auth/verify/otp/trust?device=false'

SIGNOUT_RE = re.compile("""<button onclick=["']goToLogout\(\)["'] |"""
                        """<a href=["']https://www.qtrade.ca/security/logout["'] id=["']investorLogin["']""")

test_logout_extract = """
                    </ul>
                    <div class="header-cta">
                        
                        <!-- login button -->
                            
                                
                                <a href='https://www.qtrade.ca/security/logout' id="investorLogin" class="btn btn-sm3">Sign out</a>
                            
                        
                    </div>
                </div>
            </div>
"""

test_logout_extract2 = """
<div class="header-cta">
                    <!-- not logged in -->
                    
                    <!-- logged in -->
                    
                        <button onclick="goToLogout()" class="btn-login btn btn-sm4">Sign out</button>
                    
                </div>
"""

test_token_extract = """

            <p class="otpResend hidden" role="alert">
                <ion-icon name="checkmark-circle"></ion-icon>&nbsp;&nbsp;<strong>A new authentication code has been sent to to your mobile number.<br>Please make sure you are connected to a cellular network.</strong>
            </p>

            <br aria-hidden="true"><br aria-hidden="true">
        <div>
<input type="hidden" name="_csrf" value="706a3ba6-9d20-4843-bc46-f6cd76397d69" />
</div></form>
    </div>
    </div>
"""


def get_auth_token(html):
    match = CSRF_RE.findall(html)
    if not match:
        return None
    return match[0]


def has_logout_button(html):
    if SIGNOUT_RE.search(html):
        return True
    else:
        return False

def get_otp_prompt(html):
    if OTP_POST_RE.findall(html):
        token = get_auth_token(html)
        if not token:
            raise Exception("Expected OTP page to present authorization token")
        return token
    else:
        return None


def run_auth(username, password):
    """returns a logged in sessions object"""
    loginpage = requests.get(QTRADE_BASE_URL + "/security")
    
    token = get_auth_token(loginpage.text)
    if not token:
        raise Exception("Expected login page to present authorization token")
    else:
        log.debug("token %s", token)
    
    session = requests.session()

    post_data = {
            'username': username,
            'password': password,
            '_csrf': token
    }

    # this will trigger 2-factor Auth (SMS), if enabled
    homepage = session.post(QTRADE_BASE_URL + "/security/", data=post_data)

    if not has_logout_button(homepage.text):
        raise Exception("Login Failed. Double check username or password." + homepage.text)

    token = get_otp_prompt(homepage.text)

    if not token:
        raise Exception("NO TOKEN?" + homepage.text.encode('utf-8', 'ignore'))

    if token:
        # 2FA enabled
        otp = input("Enter OTP code:")
        print(repr(otp))
        secured = session.post(QTRADE_BASE_URL + "/security/qi/security-auth/verify/otp",
            data= {
                'otp': otp,
                '_csrf': token 
            }
        )
        token = get_otp_prompt(secured.text)
        if token:
            raise Exception("Invalid token provided")
        
        # reload the homepage -- do not trust this device
        homepage = session.get("https://www.qtrade.ca/security/qi/security-auth/verify/otp/trust?device=false")

        if not has_logout_button(homepage.text):
            raise Exception("2FA flow did not complete successfully: " + homepage.text.encode('utf8', 'ignore'))

    log.info("login succeeded. obtained homepage.")
    save_response(homepage)
    return session


if __name__ == "__main__":
    run_auth()
