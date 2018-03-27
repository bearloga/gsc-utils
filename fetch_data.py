#!/usr/bin/python3

import os
import sys
import datetime as dt
import argparse
import httplib2
import numpy as np
import pandas as pd

from apiclient import errors
from apiclient.discovery import build
from oauth2client.file import Storage

# Helper function:
def critical(message):
    print('ERROR: ' + message)
    sys.exit(1)

# Establish command-line arguments:
parser = argparse.ArgumentParser(description='Fetch Google Search Console statistics for a property.')
parser.add_argument("credentials", help="Use custom credentials file")
parser.add_argument("website",
                    help="Web property to fetch stats about; e.g. en.wikipedia.org, commons.wikimedia.org")
parser.add_argument("split", choices=['none', 'country', 'device', 'country-device'], default='none',
                    help="Dimension to split by, if any")
parser.add_argument("outdir", help="path/to/directory to store output in")
parser.add_argument("date", nargs="?", default=dt.date.today().strftime("%Y-%m-%d"),
                    help="Date (YYYY-MM-DD) to fetch data for (default: %(default)s (today))")
parser.add_argument("days", type=int, default=0, nargs="?",
                    help="Days to fetch, up to 90; useful for back-filling (default: %(default)s)")
parser.add_argument("-r", "--rich", action="store_true", help="Fetch stats for results appearing as rich cards")
parser.add_argument("--http", action="store_true",
                    help="Fetch stats about the non-secure variant (https is used by default)")
parser.add_argument("-v", "--verbose", action="store_true", help="Increase output verbosity")
args = parser.parse_args()
# dev/debug: ['-v', '-r', 'cache/creds-mpopov.json', 'en.wikipedia.org', 'none', 'output/enwiki', '2018-03-01', '90']

# Create the URL to be used with the request:
if args.http:
    website_url = "http://" + args.website + '/'
else:
    website_url = "https://" + args.website + '/'

# Create the start of the data range:
try:
    start_date = dt.datetime.strptime(args.date, '%Y-%m-%d') - dt.timedelta(days=args.days)
except ValueError:
    critical('Invalid %s.' % args.date)

# Create an httplib2.Http object and authorize it with saved credentials:
if args.verbose:
    print("Loading credentials from " + args.credentials)

storage = Storage(args.credentials)
credentials = storage.get()
http = httplib2.Http()
http = credentials.authorize(http)

# refer to developers.google.com/resources/api-libraries/documentation/webmasters/v3/python/latest/
#   webmasters_v3.searchanalytics.html for more information
webmasters_service = build('webmasters', 'v3', http=http)
def execute_request(site_url, request):
   return webmasters_service.searchanalytics().query(siteUrl = site_url, body = request).execute()

# Construct API request:
request = {
    'startDate': start_date.strftime("%Y-%m-%d"),
    'endDate': args.date
}

if args.rich:
    request['dimensionFilterGroups'] = [{
        'filters': [{
            'dimension': 'searchAppearance',
            'expression': 'RICHCARD'
        }]
    }]

if args.split == 'country':
    request['dimensions'] = ['date', 'country']
elif args.split == 'device':
    request['dimensions'] = ['date', 'device']
elif args.split == 'country-device':
    request['dimensions'] = ['date', 'country', 'device']
else:
    request['dimensions'] = ['date']

if args.verbose:
    print("Requesting the following info about '" + website_url + "':")
    print(request)

response = execute_request(website_url, request)

if not response.__contains__('rows'):
    critical('No data returned by the API')

# Get a DataFrame into a writeable format:
df = pd.DataFrame.from_dict(response['rows'])
df['date'] = df['keys'].apply(lambda x: x[0])
df['clicks'] = df['clicks'].astype(np.int64)
df['impressions'] = df['impressions'].astype(np.int64)

if args.split == 'country':
    df['country'] = df['keys'].apply(lambda x: x[1].upper())
    df = df[['date', 'country', 'clicks', 'impressions', 'ctr', 'position']]
    df = df.sort_values(by = ['date', 'country'], ascending=[True, True])
elif args.split == 'device':
    df['device'] = df['keys'].apply(lambda x: x[1].capitalize())
    df = df[['date', 'device', 'clicks', 'impressions', 'ctr', 'position']]
    df = df.sort_values(by=['date', 'device'], ascending=[True, True])
elif args.split == 'country-device':
    df['country'] = df['keys'].apply(lambda x: x[1].upper())
    df['device'] = df['keys'].apply(lambda x: x[2].capitalize())
    df = df[['date', 'country', 'device', 'clicks', 'impressions', 'ctr', 'position']]
    df = df.sort_values(by=['date', 'country', 'device'], ascending=[True, True, True])
else:
    df = df[['date', 'clicks', 'impressions', 'ctr', 'position']].sort_values(by = ['date'], ascending=True)

# Create output directory if it does not exist yet:
if not os.path.exists(args.outdir):
    os.makedirs(args.outdir)

output_filename = args.outdir + '/' + ("overall" if args.split == 'none' else args.split)
output_filename += '-' + ("rich" if args.rich else "all") + '.csv'

df.to_csv(output_filename, index=False, float_format='%.4f', mode='a', header=not os.path.exists(output_filename))
