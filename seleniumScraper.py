# Author: Evangelos Dimitriadis
# This script is finds bitcoin addresses in youtube comments.
# The script uses Selenium and geckodriver. See README for more details.

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from pprint import pprint
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import sys
import re
import json

def findBitcoins(line):
	searchObj = re.search("([']?)[123mn][a-km-zA-HJ-NP-Z1-9]{26,33}([']?)", line)
	return searchObj

def scrollDown(driver):
	scrollPauseTime = 5
	# Get scroll height
	last_height = driver.execute_script("return document.body.scrollHeight")
	while True:
		# That try-except chunk of code is beta. Gets every reply, it works but needs more testing.
		"""
		try:
			for i in driver.find_elements_by_class_name("load-more-text"):
				i.click()
				time.sleep(scrollPauseTime)
		except Exception as e:
			pass
		"""
		# Scroll down to bottom
		driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		# Wait to load page
		time.sleep(scrollPauseTime)
		# We need to push the button to find more comments. This might change in the near future.
		driver.find_element_by_xpath('/html/body/div[2]/div[4]/div/div[5]/div[2]/div[2]/div/div[2]/div[5]/div/button').click()
		# Calculate new scroll height and compare with last scroll height
		new_height = driver.execute_script("return document.body.scrollHeight")
		if new_height == last_height:
		    break
		last_height = new_height

def main():
	try:
		profile = webdriver.FirefoxProfile()
		# User agent of Chrome
		profile.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36")
		options = Options()
		options.set_headless(headless=True) # Remove if you want to see the Selenium in action
		driver = webdriver.Firefox(profile,firefox_options=options)
		driver.get("https://www.youtube.com/watch?v=aJmeouLNlpY")
		# A good example to test the replies chunk of code in def scrollDown.
		# Test without headless=True. Use at your own risk.
		#driver.get("https://www.youtube.com/watch?v=s9YbICd43Mc")
		pprint(driver.current_url)
		time.sleep(5)
		scrollDown(driver)
	
		for item in driver.find_elements_by_class_name("comment-renderer-content"):
			#print(item.get_attribute('innerHTML'))
			lines = item.get_attribute('innerText').splitlines()
			#print(lines[1]) #This is the comment
			matchObj = findBitcoins(lines[1])
			if matchObj:
				dictionary = {'BitcoinAddress' : matchObj.group(0),'User' : lines[0] ,'Source' : driver.current_url}
				with open('comments2.json', 'a') as outfile:
					json.dump((dictionary), outfile,indent=4)
		
	finally:	# Be sure to kill Selenium after the job is done
	    driver.quit()

if __name__ == '__main__':
    sys.exit(main())