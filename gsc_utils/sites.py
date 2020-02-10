import numpy as np
import pandas as pd
from googleapiclient.discovery import build

from gsc_utils import utils


def list(credentials):
    """
    Fetch list of properties registered in Google Search Console

    :param credentials: Pre-authorized credentials, loaded using `utils.load_credentials()`
    :return: Pandas DataFrame with column 'siteUrl'

    See https://developers.google.com/webmaster-tools/search-console-api-original/v3/sites/list for more info
    """

    # Make the API request:
    webmasters_service = build('webmasters', 'v3', http=credentials)
    site_list = webmasters_service.sites().list().execute()

    # Tidy up and output:
    df = pd.DataFrame.from_dict(site_list['siteEntry'])
    return df[['siteUrl']].sort_values(by=['siteUrl'], ascending=True)


def add(credentials, website):
    """
    Register 1+ properties in Google Search Console, if the API credentials have sufficient authentication scope

    :param credentials: Pre-authorized credentials, loaded using `utils.load_credentials()`
    :param website: Full URL (e.g. 'https://commons.m.wikimedia.org/') or list of full URLs
    :return: Responses, one for each requested website addition

    See https://developers.google.com/webmaster-tools/search-console-api-original/v3/sites/add for more info.
    """
    # refer to developers.google.com/resources/api-libraries/documentation/webmasters/v3/python/latest/
    #   webmasters_v3.searchanalytics.html for more information
    webmasters_service = build('webmasters', 'v3', http=credentials)

    if type(website) == str:
        website = [website]

    responses = []
    for site_url in website:
        response = webmasters_service.sites().add(siteUrl=site_url).execute()
        responses.append(response)
    return responses


def remove(credentials, website):
    """
    Un-register 1+ properties in Google Search Console, if the API credentials have sufficient authentication scope

    :param credentials: Pre-authorized credentials, loaded using `utils.load_credentials()`
    :param website: Full URL (e.g. 'https://commons.m.wikimedia.org/') or list of full URLs
    :return: Responses, one for each requested website deletion

    See https://developers.google.com/webmaster-tools/search-console-api-original/v3/sites/delete for more info.
    """
    # refer to developers.google.com/resources/api-libraries/documentation/webmasters/v3/python/latest/
    #   webmasters_v3.searchanalytics.html for more information
    webmasters_service = build('webmasters', 'v3', http=credentials)

    if type(website) == str:
        website = [website]

    responses = []
    for site_url in website:
        response = webmasters_service.sites().delete(siteUrl=site_url).execute()
        responses.append(response)
    return responses
