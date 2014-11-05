#!/usr/bin/env python
import sys
import string
from restkit import OAuthFilter, request    # http reading
import oauth2                                # oauth2 framework
import simplejson as json                    # json reader
#import dateutil.parser as dateparse            # date processing
from operator import itemgetter                # list processing
import csv                                    # csv file processing

from private_keys import KEYS

STOCK_URL = 'https://api.tradeking.com/v1/market/ext/quotes.json'

def tk_query(queryurl, returntype='json'):
    # key and secret granted by service provider for this consumer application
    CONSUMER_KEY       = KEYS.CONSUMER_KEY
    CONSUMER_SECRET    = KEYS.CONSUMER_SECRET
    OAUTH_TOKEN_KEY    = KEYS.OAUTH_TOKEN_KEY 
    OAUTH_TOKEN_SECRET = KEYS.OAUTH_TOKEN_SECRET 


    # set up an OAuth Consumer
    myconsumer = oauth2.Consumer(key=CONSUMER_KEY, secret=CONSUMER_SECRET)
    # manually update the access token/secret.
    mytoken = oauth2.Token(key=OAUTH_TOKEN_KEY, secret=OAUTH_TOKEN_SECRET)
    # make an oauth request
    auth = OAuthFilter('*', consumer=myconsumer, token=mytoken,
    method = oauth2.SignatureMethod_HMAC_SHA1())
    # get the response and return it
    queryresp = request(queryurl, 'GET', filters=[auth])
    if returntype == 'json':
        queryresult = json.loads(queryresp.body_string())
    else:
        queryresult = queryresp.body_string()
    return queryresult
    
def stock_query(ticket,returntype='json'):
    query = tk_query(STOCK_URL+'?symbols='+ticket,returntype)
    try:
        price = query['response']['quotes']['quote'].get('last')
        return price
    except TypeError:
        return None
    
def main():
    if len(sys.argv) < 2:
        print >> sys.stdout, "Usage: %s <ticket>" %sys.argv[0]
        exit()
    else:
        for ticket in sys.argv[1:]:
            price = stock_query(ticket,'json') # there is a bug in json parser
            print >> sys.stdout, "%5s Last price: %s" %(ticket,price)
            
if __name__ == "__main__":
    main()
