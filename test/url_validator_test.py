import validators
from urllib.parse import urlparse
from urllib3.util import Url, parse_url
import urllib3
import re



from pprint import pprint

valid_urls = [
    'https://www.google.com',
    'https://***REMOVED***.com/job/***REMOVED***/job/Transfers/job/bmm-acl/job/master/',
    'https://retailjenkins:5000/job/***REMOVED***/job/Transfers/job/bmm-acl/job/master/',
    'https://128.0.0.1:5000/job/***REMOVED***/job/Transfers/job/bmm-acl/job/master/',
    '128.0.0.1:5000/job/***REMOVED***/job/Transfers/job/bmm-acl/job/master/',
    'http://jenksintest:5000',
    'http://jenksintest:5000',
    'udp://jenksintest:5000',
    'http:jenksintest:5000',
    'http/jenksintest:5000',
    'jenkinstest:5000'
]

for url in valid_urls:
    print('\n\n\n------------------------------------------------------------')
    print(url)
    print('------------------------------------------------------------')
    print('validators.url() - ', validators.url(url) == True)
    print('validators.ip_address.ipv4() - ', validators.ip_address.ipv4(url) == True)
    print('')
    # print('urlparse() - ', urlparse(url))
    print('scheme  : ', urlparse(url).scheme)
    print('netloc  : ', urlparse(url).netloc)
    print('path    : ', urlparse(url).path)
    print('port    : ', urlparse(url).port)
    print('schema (string): ', re.findall('(\w+)://', url))
    # print(all([urlparse(url).scheme, urlparse(url).netloc, urlparse(url).path]))
    # print(parse_url(url), parse_url(url).scheme, parse_url(url).netloc, parse_url(url).path, parse_url(url).port)

