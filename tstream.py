#!/usr/bin/env python

import tweepy
import json
import sys
import re
import os
from lxml import html
from urllib2 import urlopen
from fnmatch import fnmatch

consumer_key = ''
consumer_secret = ''
access_token = ''
access_token_secret = ''
pictureCounter = 0
tweetCounter = 0
pictureList = ['']*20

# This is the listener, resposible for receiving data
class StdOutListener(tweepy.StreamListener):
	try:  
		def on_data(self, data):
			# Twitter returns data in JSON format - we need to decode it first
			decoded = json.loads(data)
			global pictureCounter
			global tweetCounter
			# Also, we convert UTF-8 to ASCII ignoring all bad characters sent by users
			try:
				message = decoded['text'].encode('ascii', 'ignore')
				tweetCounter += 1
				url = re.search("(?P<url>https?://[^\s]+)", message)	
				if url:
					try:
						url = url.group("url")
						print '%s %s' %(tweetCounter, url)
						page = urlopen('%s'%url)
						page_source = html.parse(page)
						list = page_source.xpath('//img/@src')
						match = [s for s in list if "pbs.twimg.com/media/" in s]
						if match:
							if '.jpg' in match[0]:
								if uniquePictureCheck(pictureCounter, match[0]):
									print('%s' %(match[0])),	
									print('saved as picture%01d.jpg' %pictureCounter),
									print('from: @%s' %(decoded['user']['screen_name'])),
									print('link: %s' %url)
									os.system("wget -O picture%01d.jpg %s --quiet" %(pictureCounter,match[0]))
									pictureCounter += 1
									if pictureCounter == 20:
										pictureCounter = 0
								else:
									print('Duplicate picture %s at %s' %(match[0], url))
					except:
						pass
	
			except:
				pass	
			
			return True
		def on_error(self, status):
			print 'Status error code:',
			print status

	except:
		print 'something went wrong'

def uniquePictureCheck(listIndex, url):

	global pictureList

	if url in pictureList:
		return False
	else:
		pictureList[listIndex] = url
		return True
	

if __name__ == '__main__':
    l = StdOutListener()
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    hashtag = sys.argv[1]
    os.system("rm *.jpg")
    print "Saving unique jpg pics from tweets tagged with #%s:" %(hashtag)

    # There are different kinds of streams: public stream, user stream, multi-user streams
    # For more details refer to https://dev.twitter.com/docs/streaming-apis
    stream = tweepy.Stream(auth, l)
    stream.filter(track=['%s'%(hashtag)])
    

