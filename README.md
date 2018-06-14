# GSC Data Fetcher

Utility for accessing and downloading the statistics on a site's presence in Google's search results via [Search Console API](https://developers.google.com/webmaster-tools/search-console-api-original/).

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
python3 fetch_stats.py path/to/credentials SITE SPLIT path/to/output DATE DAYS
```

**Note**: that since Google doesn't store more than 90 days of Search Console reports, be careful choosing `DATE` and `DAYS`.

HTTPS is assumed but an HTTP variant of a property is supported:

```bash
python3 fetch_stats.py --http path/to/credentials SITE SPLIT path/to/output
```

See `./fetch_stats.py --help` for more information. **Note**: according to [official documentation](https://developers.google.com/webmaster-tools/search-console-api-original/v3/searchanalytics/query#dimensionFilterGroups.filters.dimension), country codes are returned as [ISO 3166-1 alpha-3](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3).

### Example

```bash
virtualenv -p /usr/bin/python3 myenv
source myenv/bin/activate
git clone https://github.com/bearloga/wmf-gsc.git gsc
pip install -U -r gsc/requirements.txt
```

…steps to authorize and save credentials…

```bash
python fetch_stats.py --rich cache/creds-mpopov.json en.wikipedia.org none output/enwiki 2018-03-24 90
```

### Rich Card Results

Some results appear as rich cards in Google's search results, and the way the statistics are calculated is different. Specifically, there are two aggregation types: by site and by page. When the `--rich` flag is present, the statistics returned will be aggregated _by page_. Otherwise all results will be considered and the aggregation will be _by site_.

Refer to [Aggregating data by site vs by page](https://support.google.com/webmasters/answer/6155685?authuser=0#urlorsite) for details.

## Site List

To create a text file listing the properties available under the account:

```
python3 fetch_sitelist.py path/to/credentials sites.txt
```
