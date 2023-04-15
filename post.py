import random

import base64
import io
from PIL import Image

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import cv2
import pytesseract

from bot_studio import *

# from youtube_uploader_selenium import YouTubeUploader


def downloadImage(url):
	shortUrl = url[url.find('/9'):]
	im = Image.open(io.BytesIO(base64.b64decode(shortUrl))).save('thumbnail.png')

def checkImageHasText(path):
	img = cv2.imread(path)   
	text = pytesseract.image_to_string(img)
	return False if text == "" else True



def getThumbnails(input):
	input = input.replace(" ", "")
	url = "https://www.google.co.in/search?q=funny+" + input + "+youtube&source=lnms&tbm=isch"


	options = webdriver.ChromeOptions()
	options.add_argument('--headless')

	driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
	driver.get(url)
	pageText = driver.page_source
	driver.close()

	linksArray = []

	LINK_START = '<img src="'
	EXCLUDE_IMAGE_LIST = ["data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAq0lEQVQ4jaWT0Q2DMAxEXyIGYAMygkdgBTZgRDaAETpC2CAbXD+giKoJbYklK4niO8tn20mixnwVGmiOm3MtYPurL8Qv+/lASgBIQjAK9KePkkBgN8AvNw+ECgnMn+r+tBihL8kBQLjuQtfBPMM0QQjZkN/a2LbFr2uCdYVh2MqIMRvSAI8igRmkdJUieiBPDd/AsA1U3SC5Y5neR9mAnHLLKXMCTgQ3rXobnzl8hRUj722/AAAAAElFTkSuQmCC"]
	
	while True:
		if (pageText.find(LINK_START) == -1):
			break
		else:
			startIndex = pageText.find(LINK_START)
			endIndex = pageText.find('"', startIndex+len(LINK_START))

			link = pageText[startIndex+len(LINK_START):endIndex]
			pageText = pageText[endIndex:]

			if not link in EXCLUDE_IMAGE_LIST:
				linksArray.append(link)


	while True:
		randomLink = random.choice(linksArray)
		downloadImage(randomLink)

		if not checkImageHasText("thumbnail.png"):
			break


def post():

	cookiesFile = open("cookies.txt", "r")
	cookiesData = cookiesFile.read()
	cookiesList = cookiesData.split("\n")
	cookiesFile.close()

	youtube = bot_studio.youtube()
	youtube.login_cookie(cookies=cookiesList)

	response = youtube.upload(title='test', video_path='/Users/ben/Desktop/secretProject/Videos/intro.mp4', kid_type="Yes, it's made for kids", description='description', type='Private')









getThumbnails("dog")
post()

















