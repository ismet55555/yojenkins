from urllib.parse import urlencode, urlparse, urlsplit, urlunparse, urljoin
from pprint import pprint

# 1. urlparse
# 2. .split the path variable
# 3. remove last item (check for number)
# 4. Join the list
# 5. Join everything back together
# 6. Add a / at the very end of the url


url = 'https://***REMOVED***.com/job/***REMOVED***/job/Non-Prod-Jobs/job/***REMOVED***/job/test_job/13'
print(url)

# Dissect the build url
url_parsed = urlparse(url)
path_list = url_parsed.path.split('/')

# Remove the build number
last_index = -2 if not path_list[-1] else  -1
path_new = '/'.join(path_list[0:last_index]) 

# Assemble the job url
base_url = url_parsed.scheme + '://' + url_parsed.netloc
final = urljoin(base_url, path_new)

pprint(final)