# gsc-utils

Utilities for accessing and downloading the statistics on a site's presence in Google's search results via [Search Console API](https://developers.google.com/webmaster-tools/search-console-api-original/).

## Setup

```bash
pip3 install -U git+https://github.com/bearloga/gsc-utils.git
```

### Credential authorization

Create a OAuth 2.0 Client ID on the [Credentials page](https://console.developers.google.com/apis/credentials) of the API console. Then download the secrets JSON. You will use this to create and save a set of authorized credentials. When run, the code will ask you to navigate to a specific URL to authorize with your Google account and prompt you for a verification code which you will be given after approving the authorization request.

```python
from gsc_utils import utils

creds = utils.authorize('path/to/secrets.json')
utils.save_credentials(creds, 'path/to/credentials.json')
```

The created `credentials.json` should look similar to [this sample](cache/credentials-sample.json). You can re-use it in future sessions without having to re-authorize:

```python
from gsc_utils import utils

creds = utils.load_credentials('path/to/credentials.json')
```

**Note**: Some of the code has been adapted from [Quickstart: Run a Search Console App in Python ](https://developers.google.com/webmaster-tools/search-console-api-original/v3/quickstart/quickstart-python) and [OAuth 2.0 Storage](https://developers.google.com/api-client-library/python/guide/aaa_oauth#storage).

## Usage

To fetch and save a list of properties registered in GSC for the user whose credentials are being used:

```python
from gsc_utils import fetch

site_list = fetch.sitelist(creds)
site_list.to_csv('path/to/sites.csv', index=False)
```

It is important to get stats only for sites in that list. Here is an example of getting stats (impressions, clicks, average position) for English Wikipedia desktop and mobile web sites:

```bash
from gsc_utils import fetch

enwiki = fetch.stats(creds, 'en.wikipedia.org', '2020-01-01', '2020-01-31')
enwiki['variant'] = 'desktop'
enwiki_mobile = fetch.stats(creds, 'en.m.wikipedia.org', '2020-01-01', '2020-01-31')
enwiki_mobile['variant'] = 'mobile web'

enwiki = enwiki.append(enwiki_mobile)
```

**Note**: When `split_by='country'` or `split_by='country-device'`, country codes are returned as [ISO 3166-1 alpha-3](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3) (according to [official documentation](https://developers.google.com/webmaster-tools/search-console-api-original/v3/searchanalytics/query#dimensionFilterGroups.filters.dimension)).

### Rich Card Results

Some results appear as rich cards in Google's search results, and the way the statistics are calculated is different. Specifically, there are two aggregation types: by site and by page. When `rich_results=True`, the statistics returned will be aggregated _by page_. Otherwise all results will be considered and the aggregation will be _by site_.

Refer to [Aggregating data by site vs by page](https://support.google.com/webmasters/answer/6155685?authuser=0#urlorsite) for details.

### Example usage in R

```R
# install.packages(c("purrr", "urltools", "readr", "reticulate"))

library(reticulate)

gsc_utils <- import("gsc_utils.utils")
fetch <- import("gsc_utils.fetch")

creds <- gsc_utils$load_credentials('path/to/credentials.json')

site_list <- fetch$sitelist(creds)

results <- purrr::map_dfr(
  site_list$siteUrl,
  function(site_url, start, end) {
    website <- urltools::domain(site_url)
    use_https <- urltools::scheme(site_url) == "https"
    result <- fetch$stats(creds, website, start, end, use_https = use_https)
    return(result)
  },
  start = "2020-01-01", end = "2020-01-31"
)

readr::write_csv(results, "stats_2020-01.csv")
```

**Note**: If `gsc-utils` is installed in a different virtual environment than the default one, include the following in .Rprofile in working directory:

```R
Sys.setenv(RETICULATE_PYTHON = "path/to/python")
```

Refer to [Python Version Configuration](https://rstudio.github.io/reticulate/articles/versions.html) for more instructions and details.
