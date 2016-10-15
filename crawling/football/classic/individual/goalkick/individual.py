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
game_type=1
no =7
while True:
	if year == 2017:
		break
	for i in range(1,2):
		page_url = 'http://www.kleague.com/KOR_2016/record/data_3.asp?year='+str(year)+'&game=1&sType=0'+str(no)
		url_open = urllib.request.urlopen(page_url)
		soup = BeautifulSoup(url_open, 'html.parser', from_encoding = 'utf-8')
		td_list = soup.select(".table1 td")

		with open(str(year)+"_individual0"+str(no)+".csv","w") as f:	
			writer= csv.writer(f)
			writer.writerow(["no","name","team","goalKick","numOfGame","GoalKickPerGame"])
			out=[]
			for i in range(len(td_list)):
				if i is not 0 and i%6 == 0:
					writer.writerow(out)
					out=[]
				out.append(td_list[i].text)
			

			
	year=year+1
