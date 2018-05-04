# Author: Evangelos Dimitriadis
# The script uses the official youtube API, provided by google, to find similar youtube video IDs.


import sys
import urllib.request
import json
import pprint
import re
import logging

APIkey = "AIzaSyDMT-jhXXO26Tyi-q1_6dst2y2xP-jzOfc"

def checkURL(url):
	youtubeRegex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
	matchRegex = re.match(youtubeRegex, url)
	if matchRegex:					# Return only the videoID
		return matchRegex.group(6)
	else:							# It should be already a videoID
		return url 

def sendRequest(search):
	try:
		with urllib.request.urlopen(search) as http:
			data = json.load(http)
			return data
	except urllib.error.URLError as e:
		print(e.reason)
		return(-1)

def relatedVideos(videoID,maxResults):
	apiRelated = "https://www.googleapis.com/youtube/v3/search?part=snippet&relatedToVideoId="
	search = apiRelated + videoID + "&maxResults=" + str(maxResults) + '&type=video' +'&key=' + APIkey 
	data = sendRequest(search)
	if data == -1:
		return(-1)
	ListOfVideos = set()
	for i in range(0,maxResults):
		ListOfVideos.add(data.get('items', {})[i]['id']['videoId'])
	return ListOfVideos

def main():
	# The number of the videos that the script will try to find	
	maxResults = 30
	# This is a great video ID example
	url = 'aJmeouLNlpY'
	print("The video ID is: " + checkURL(url))
	videoID = checkURL(url)
	IDs = relatedVideos(videoID,maxResults)

	outfile = open('ListOfVideos.txt', 'a')
	for item in IDs:
		outfile.write("%s\n" % item)

if __name__ == '__main__':
    sys.exit(main())
