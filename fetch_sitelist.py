import argparse
import httplib2
import pandas as pd

from apiclient import errors
from apiclient.discovery import build
from oauth2client.file import Storage

parser = argparse.ArgumentParser(description='Fetch Google Search Console statistics for a property.')
parser.add_argument("credentials", help="path/to/credentials (pre-authorized, see README)")
parser.add_argument("outfile", default='sites.txt',
                    help="path/to/directory to store output in (default: %(default)s)")
args = parser.parse_args()
# dev/debug: ['cache/creds-noc.json', 'sites.txt']

storage = Storage(args.credentials)
credentials = storage.get()
http = httplib2.Http()
http = credentials.authorize(http)

webmasters_service = build('webmasters', 'v3', http=http)

site_list = webmasters_service.sites().list().execute()
df = pd.DataFrame.from_dict(site_list['siteEntry'])
df[['siteUrl']].sort_values(by = ['siteUrl'], ascending=True).to_csv(args.outfile,index=False)
