import sys

import httplib2
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage


def print_err(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def critical(msg):
    print('ERROR: ' + msg)
    sys.exit(1)


def authorize(secrets_json):
    """
    Authorize a set of credentials for use and re-use

    :param secrets_json: Path to secrets JSON downloaded from API console
    :return: An `httplib2.Http` object, authorized with credentials
    """
    flow = flow_from_clientsecrets(secrets_json,
                                   scope='https://www.googleapis.com/auth/webmasters.readonly',
                                   redirect_uri='urn:ietf:wg:oauth:2.0:oob')
    # Create an httplib2.Http object and authorize it with our credentials
    authorize_url = flow.step1_get_authorize_url()
    print('Go to the following link in your browser: ' + authorize_url)
    code = input('Enter verification code: ').strip()
    credentials = flow.step2_exchange(code)
    http = httplib2.Http(cache="cache")
    http = credentials.authorize(http)
    return http


def save_credentials(credentials, credentials_json):
    """
    Authorize and save credentials for re-use

    :param credentials: Authorized credentials created with `authorize()`
    :param credentials_json: Path to save authorized credentials to
    """
    storage = Storage(credentials_json)
    storage.put(credentials)
    return None


def load_credentials(credentials_json):
    """
    Create an httplib2.Http object and authorize it with saved credentials

    :param credentials_json: Path to pre-authorized credentials (saved with `authorize`)
    :return: An `httplib2.Http` object, authorized with credentials
    """
    storage = Storage(credentials_json)
    credentials = storage.get()
    http = httplib2.Http()
    http = credentials.authorize(http)
    return http
