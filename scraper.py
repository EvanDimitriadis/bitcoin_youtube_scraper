# Author: Evangelos Dimitriadis
# The script uses the official youtube API, provided by google, to find bitcoin addresses.

import sys
import urllib.request
import json
import pprint
import re
import logging

APIkey = "AIzaSyDMT-jhXXO26Tyi-q1_6dst2y2xP-jzOfc"

def item_generator(json_input, lookup_key):
    if isinstance(json_input, dict):
        for k, v in json_input.items(): 
            if k == lookup_key:
                yield v
            else:
                for child_val in item_generator(v, lookup_key):
                    yield child_val
    elif isinstance(json_input, list): # This generator also searches in the lists of dictionaries
        for item in json_input:
            for item_val in item_generator(item, lookup_key):
                yield item_val

def findBitcoins(line):
	searchObj = re.search("([']?)[123mn][a-km-zA-HJ-NP-Z1-9]{26,33}([']?)", line)
	return searchObj

def checkURL(url):
	youtubeRegex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
	matchRegex = re.match(youtubeRegex, url)
	if matchRegex:					# Return only the videoID
		return matchRegex.group(6)
	else:							# It should be the videoID
		return url 

def sendRequest(search):
	try:
		with urllib.request.urlopen(search) as http:
			data = json.load(http)
			return data
	except urllib.error.URLError as e:
		print(e.reason)
		return(-1)

def findDescription(videoID):

	apiVideos = "https://www.googleapis.com/youtube/v3/videos?part=snippet&id="
	search = apiVideos + videoID + '&key=' + APIkey 
	data = sendRequest(search)
	if data == -1:
		return(-1)

	for description in item_generator(data,'snippet'):
		text = description['description']
		matchObj = findBitcoins(text)
		if matchObj:
			bitcoinString = {'BitcoinAddress: ' : matchObj.group(0)} # It's actually a small dictionary, just to dump it correctly.
			with open('description.json', 'a') as outfile:
				json.dump(( (bitcoinString , description)), outfile,indent=4)

def findComments(videoID):
	apiCommentThreads = "https://www.googleapis.com/youtube/v3/commentThreads?part=snippet,replies&videoId="
	search = apiCommentThreads + videoID + "&maxResults=50" + '&key=' + APIkey 	# maxResults is 50 just to be sure that we do not exceed the data cap during debugging
	data = sendRequest(search)
	if data == -1:
		return(-1)

	for comment in item_generator(data,'snippet'):
		try:
			if 'topLevelComment' in comment:
				text = comment['topLevelComment']['snippet']['textDisplay']
				matchObj = findBitcoins(text)
				if matchObj:
					bitcoinString = {'BitcoinAddress: ' : matchObj.group(0)} # It's actually a small dictionary, just to dump it correctly.
					with open('comments.json', 'a') as outfile:
						json.dump(( (bitcoinString , comment['topLevelComment']['snippet'])), outfile,indent=4)
			elif 'textDisplay' in comment:									 # This is a reply to a top comment. However we do not log all replies.
				text = comment['textDisplay']
				matchObj = findBitcoins(text)
				if matchObj:
					bitcoinString = {'BitcoinAddress: ' : matchObj.group(0)} # It's actually a small dictionary, just to dump it correctly.
					with open('comments.json', 'a') as outfile:
						json.dump(( (bitcoinString , comment)), outfile,indent=4)
		except Exception as exception:
        	# Output unexpected Exceptions.
			logging.exception(exception, False)

def main():
	url = 'aJmeouLNlpY'
	#url = "https://www.youtube.com/watch?v=yK58EX4RZxA&feature=youtu.be&list=PLbYZp8RGbKd2W7Sh2TWojHzWNVk-kvxak"
	print("The video ID is: " + checkURL(url))
	videoID = checkURL(url)
	findComments(videoID)
	findDescription(videoID)

if __name__ == '__main__':
    sys.exit(main())
