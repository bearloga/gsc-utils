import numpy as np
import pandas as pd
from googleapiclient.discovery import build

from gsc_utils import utils


def sitelist(credentials):
    """
    Fetch list of properties registered in Google Search Console

    :param credentials: Pre-authorized credentials, loaded using `utils.load_credentials()`
    :return: Pandas DataFrame with column 'siteUrl'
    """

    # Make the API request:
    webmasters_service = build('webmasters', 'v3', http=credentials)
    site_list = webmasters_service.sites().list().execute()

    # Tidy up and output:
    df = pd.DataFrame.from_dict(site_list['siteEntry'])
    return df[['siteUrl']].sort_values(by=['siteUrl'], ascending=True)


def stats(credentials, website, start_date, end_date, split_by=None, use_https=True, rich_results=False):
    """
    Fetch Google Search Console statistics for a property

    :param credentials: Pre-authorized credentials, loaded using `utils.load_credentials()`
    :param website: One or more web properties to fetch stats for; e.g. `['en.wikipedia.org', 'commons.wikimedia.org']`
    :param start_date: Date (YYYY-MM-DD) to fetch data from
    :param end_date: Date (YYYY-MM-DD) to fetch data up to
    :param split_by: Dimension to split by (if any); country codes are returned as ISO 3166-1 alpha-3
    :param use_https: Fetch stats about the secure (HTTPS) variant (set to False for non-secure variant)
    :param rich_results: Fetch stats for results appearing as rich cards (False by default)
    :return: Pandas DataFrame
    """

    # refer to developers.google.com/resources/api-libraries/documentation/webmasters/v3/python/latest/
    #   webmasters_v3.searchanalytics.html for more information
    webmasters_service = build('webmasters', 'v3', http=credentials)

    if type(website) == str:
        website = [website]

    # Create the URL to be used with the request:
    if use_https:
        site_urls = ["https://" + site + '/' for site in website]
    else:
        site_urls = ["http://" + site + '/' for site in website]

    # Construct the API request:
    request = {
        'startDate': start_date,
        'endDate': end_date,
        'rowLimit': 25000
    }

    # Stats for 'rich' (not 'all') results must be filtered:
    if rich_results:
        request['dimensionFilterGroups'] = [{
            'filters': [{
                'dimension': 'searchAppearance',
                'expression': 'RICHCARD'
            }]
        }]

    if split_by == 'country':
        request['dimensions'] = ['date', 'country']
    elif split_by == 'device':
        request['dimensions'] = ['date', 'device']
    elif split_by == 'country-device':
        request['dimensions'] = ['date', 'country', 'device']
    else:
        request['dimensions'] = ['date']

    responses = []
    for site_url in site_urls:
        response = webmasters_service.searchanalytics().query(siteUrl=site_url, body=request).execute()
        if not response.__contains__('rows'):
            utils.print_err('No data returned by the API')
        for row in response['rows']:
            row.update({"site": site_url})
        responses += response['rows']

    df = pd.DataFrame.from_dict(responses)
    df['date'] = df['keys'].apply(lambda x: x[0])
    df['clicks'] = df['clicks'].astype(np.int64)
    df['impressions'] = df['impressions'].astype(np.int64)

    # Tidy-up:
    if split_by == 'country':
        df['country'] = df['keys'].apply(lambda x: x[1].upper())
        df = df[['site', 'date', 'country', 'clicks', 'impressions', 'ctr', 'position']]
        df = df.sort_values(by=['site', 'date', 'country'], ascending=[True, True])
    elif split_by == 'device':
        df['device'] = df['keys'].apply(lambda x: x[1].capitalize())
        df = df[['site', 'date', 'device', 'clicks', 'impressions', 'ctr', 'position']]
        df = df.sort_values(by=['site', 'date', 'device'], ascending=[True, True])
    elif split_by == 'country-device':
        df['country'] = df['keys'].apply(lambda x: x[1].upper())
        df['device'] = df['keys'].apply(lambda x: x[2].capitalize())
        df = df[['site', 'date', 'country', 'device', 'clicks', 'impressions', 'ctr', 'position']]
        df = df.sort_values(by=['site', 'date', 'country', 'device'], ascending=[True, True, True])
    else:
        df = df[['site', 'date', 'clicks', 'impressions', 'ctr', 'position']]
        df = df.sort_values(by=['site', 'date'], ascending=True)

    return df
