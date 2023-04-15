from urllib.request import urlopen
import ssl
import time
import pandas as pd
import os
import random

import yt_dlp

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import speech_recognition as sr
import subprocess
from better_profanity import profanity

import os
os.environ["IMAGEIO_FFMPEG_EXE"] = "/opt/homebrew/bin/ffmpeg"
from moviepy.editor import *


linksArray = []
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

hashtag = "dog"



try:
	previous_df = pd.read_csv('/Users/ben/Desktop/secretProject/' + hashtag + ".csv")
except:
	previous_df = pd.DataFrame(columns=["link", "user", "title", "tags", "date", "like_count", "comment_count", "share_count"])



options = webdriver.ChromeOptions()
# options.add_argument('--headless')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


time.sleep(1)

def scroll(numScrolls):
	print("loading page")
	driver.get("https://www.tiktok.com/tag/" + hashtag)

	print("scrolling")
	previousHeight = driver.execute_script("return document.body.scrollHeight")
	counter = 0
	stuckScrollCounter = 0

	while True:
		time.sleep(3)

		driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		new_height = driver.execute_script("return document.body.scrollHeight")


		# Stuck scrolling
		if new_height == previousHeight:

			if stuckScrollCounter >= 4 & stuckScrollCounter < 6:
				time.sleep(10)
				print("waiting longer")
				stuckScrollCounter += 1
				continue

			elif stuckScrollCounter == 6:
				print("starting over")
				driver.get("https://www.tiktok.com/tag/" + hashtag)
				previousHeight = driver.execute_script("return document.body.scrollHeight")
				time.sleep(20)
				counter = 0
				stuckScrollCounter = 0
				continue

			print("waiting for page to load")
			time.sleep(3)
			stuckScrollCounter += 1
			continue

		# Not stuck scrolling
		counter += 1
		print(counter)
		previousHeight = new_height

		# Done scrolling
		if counter == numScrolls:
			break


def splitLinks(pageSource):
	print("splitting links")
	tempString = pageSource
	LINK_START = "https://www.tiktok.com/@"

	while True:

		if (tempString.find(LINK_START) == -1):
			break
		else:
			startIndex = tempString.find(LINK_START)
			endIndex = tempString.find('"', startIndex)

			link = tempString[startIndex:endIndex]
			tempString = tempString[endIndex:]

			if not (link in previous_df["link"].tolist()):
				linksArray.append(link)

	

scroll(2)
splitLinks(driver.page_source)


num = 2
while len(linksArray) < 30:
	linksArray = []
	print("recieved {} videos".format(len(linksArray)))
	print("not enough videos, scraping again")
	num += 2
	scroll(num)
	print("splitting again")
	splitLinks(driver.page_source)

driver.quit()
print("recieved {} videos".format(len(linksArray)))


while len(linksArray) > 15:
	linksArray.remove(random.choice(linksArray))

new_videos_df = pd.DataFrame(columns=["link", "user", "title", "tags", "date", "like_count", "comment_count", "share_count"])
new_videos_df["link"] = linksArray


def scrapeData(html, generalStartString, specificStartString, endString, startLocationOffset):

	generalStart = html.find(generalStartString)
	startIndex = html.find(specificStartString, generalStart)
	endIndex = html.find(endString, startIndex+1)
	return html[startIndex + startLocationOffset:endIndex]

print("scraping individual data")


i = 0

for link in linksArray:

	page = urlopen(link, context=ctx)
	html_bytes = page.read()
	html = html_bytes.decode("utf-8")

	# Username scrape
	new_videos_df.at[i, "user"] = scrapeData(html, 'browse-username', '>', '<', 1)

	# Title scrape
	new_videos_df.at[i, "title"] = scrapeData(html, 'tiktok-j2a19r-SpanText efbd9f0', '>', '<', 1) # NEED TO CONCATENATE SPLIT DESCRIPTIONS (TAGGING ANOTHER VIDEO)

	# Tags scrape
	new_videos_df.at[i, "tags"] = scrapeData(html, 'href="/tag', '/tag/', '"', 0) # JUST FIRST TAG, NEED TO MAKE IT A LIST

	# Date scrape
	new_videos_df.at[i, "date"] = scrapeData(html, 'browser-nickname', '<span>', '<', 6)

	# Like count scrape
	new_videos_df.at[i, "like_count"] = scrapeData(html, 'like-count', '>', '<', 1)

	# Comment count scrape
	new_videos_df.at[i, "comment_count"] = scrapeData(html, 'comment-count', '>', '<', 1)

	# Share count scrape
	new_videos_df.at[i, "share_count"] = scrapeData(html, 'share-count', '>', '<', 1)

	print("scraped {} of {}".format(i, len(linksArray)-1))
	i += 1

new_videos_df = pd.concat([previous_df, new_videos_df], ignore_index = True)

new_videos_df.to_csv(hashtag + ".csv", index = False)
new_videos_df.to_csv("/Users/ben/Desktop/" + hashtag +".csv")

path = '/Users/ben/Desktop/secretProject/Videos/'
audioPath = "/Users/ben/Desktop/secretProject/clip_audio.wav"

# subprocess.run(['ffmpeg', '-i', path + 'intro.mp4', '-c', 'copy', '-y', path + 'finalVideo.mp4'])

# Create a new yt-dlp instance
ydl_options = {'outtmpl': path + 'clip.mp4'}
ydl = yt_dlp.YoutubeDL(ydl_options)

video = VideoFileClip(path + 'intro.mp4')

# Initialize the TTS recognizer
r = sr.Recognizer()

for link in linksArray:

	# Download the TikTok video
	ydl.download([link])

	tempClip = VideoFileClip(path + 'clip.mp4')
	tempClip.audio_fadein(0.01).audio_fadeout(0.01)

	command = "ffmpeg -i " + path +"clip.mp4 -ab 160k -ac 2 -ar 44100 -vn clip_audio.wav -loglevel warning"
	subprocess.call(command, shell=True, stdout=subprocess.DEVNULL)

	try:
		with sr.AudioFile(audioPath) as source:
			# listen for the data (load audio to memory)
			audio_data = r.record(source)
			# recognize (convert from speech to text)
			transcript = r.recognize_google(audio_data)
	
		if not profanity.contains_profanity(transcript):
			video = concatenate_videoclips([video, tempClip], method="compose")
		else:
			print("found video with profanity, deleted -- link: " + link)
	except:
		video = concatenate_videoclips([video, tempClip], method="compose")

	os.remove(path + "clip.mp4")
	os.remove(audioPath)


video = concatenate_videoclips([video, outtro], method="compose")



video.write_videofile(path + "finalVideo.mp4", threads=8, fps=24, codec="libx264", preset="ultrafast", ffmpeg_params=["-crf", "24"])





