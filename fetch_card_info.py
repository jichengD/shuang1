#!/usr/bin/env python
# -*- coding:utf-8 -*-

import urllib2
import urllib
import json
import hashlib
import sys

'''
fetch bank card info
'''


card_data = {
    'card_no': '62169143016218fds',
}
url='https://www..com/api/fetchCardInfo'
secret_key = 'xxxxx'

def createSign(card_data):

    sorted_data = sorted(card_data.items(),key=lambda item:item[0])
    str = ''
    for val in sorted_data:
        str += val[0] + '=' + val[1] + '&'
    str = str.rstrip('&')
    str += secret_key
    sign = hashlib.md5(str).hexdigest()
    return sign


def getCardInfo(card_data):

    req = urllib2.Request(url)
    data = urllib.urlencode(card_data)
    #enable cookie
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
    response = opener.open(req, data)

    return json.loads(response.read())


if __name__ == '__main__':
    print '-------- four elements check card--------'
    card_data['sign'] = createSign(card_data)
    print 'request data:'
    for key,value in card_data.iteritems():
        print "\t" + key + ' : ' + value

    print '--------------------------------------------'
    response = getCardInfo(card_data)

    print json.dumps(response,sort_keys=True,indent=4, separators=(',', ': '))

