from bs4 import BeautifulSoup
import ctypes
import urllib
import urllib.request

import csv
from lxml import html
import sys


year = 1983
my_list = []
s = ""
page =1
while True:
	if year == 2017:
		break
	page_url = 'http://www.kleague.com/KOR_2016/record/data.asp?year='+str(year)+'&game=1&game_type'
	url_open = urllib.request.urlopen(page_url)
	soup = BeautifulSoup(url_open, 'html.parser', from_encoding = 'utf-8')
	td_list = soup.select(".table1 td")

	with open(str(year)+"_club.csv","w") as f:	
		writer= csv.writer(f)
		writer.writerow(["rank","club","numOfGame","winScore","win","draw","lose","score","lscore","difference"])
		out=[]
		for i in range(len(td_list)):
			if i is not 0 and i%10 == 0:
				writer.writerow(out)
				out=[]
			out.append(td_list[i].text)
			

			
	year=year+1
