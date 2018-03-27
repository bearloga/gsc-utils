# Google Search Consola Data Fetcher

Wikipedia's and other Wikimedia Foundation sites' presence in Google's search results via [Search Console API](https://developers.google.com/webmaster-tools/search-console-api-original/).

## Setup

Relies on the [Google's Python client library](https://developers.google.com/api-client-library/python/) via [google-api-python-client](https://github.com/google/google-api-python-client):

```bash
pip install -r requirements.txt
```

### Credentials

Adapted from [Quickstart: Run a Search Console App in Python ](https://developers.google.com/webmaster-tools/search-console-api-original/v3/quickstart/quickstart-python) and [OAuth 2.0 Storage](https://developers.google.com/api-client-library/python/guide/aaa_oauth#storage):

```python
import httplib2
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage

flow = flow_from_clientsecrets('client_secrets.json', scope='https://www.googleapis.com/auth/webmasters.readonly', redirect_uri='urn:ietf:wg:oauth:2.0:oob')

# Create an httplib2.Http object and authorize it with our credentials
authorize_url = flow.step1_get_authorize_url()
print('Go to the following link in your browser: ' + authorize_url)
code = input('Enter verification code: ').strip()
credentials = flow.step2_exchange(code)
http = httplib2.Http(cache="cache")
http = credentials.authorize(http)

# Save
storage = Storage('cache/credentials.json')
storage.put(credentials)
```

You should have a file that looks like [this](cache/credentials-sample.json).

## Usage

```bash
python3 fetch_data.py path/to/credentials SITE SPLIT path/to/output DATE DAYS
```

**Note**: that since Google doesn't store more than 90 days of Search Console reports, be careful choosing `DATE` and `DAYS`.

HTTPS is assumed but an HTTP variant of a property is supported:

```bash
python3 fetch_data.py --http path/to/credentials SITE SPLIT path/to/output
```

See `./fetch_data.py --help` for more information.

### Example

```bash
virtualenv -p /usr/bin/python3 myenv
source myenv/bin/activate
pip install -U -r gsc/requirements.txt
```

```bash
# source myenv/bin/activate
# cd gsc
python fetch_data.py --rich cache/creds-mpopov.json en.wikipedia.org none output/enwiki 2018-03-24 90
```
