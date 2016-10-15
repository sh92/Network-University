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
	page_url ='http://www.kleague.com/KOR_2016/record/data_4.asp?year=2016&game=1&teamId=K02' 
	url_open = urllib.request.urlopen(page_url)
	soup = BeautifulSoup(url_open, 'html.parser', from_encoding = 'utf-8')
	td_list = soup.select(".table1 td")

	with open(str(year)+"_teamK02.csv","w") as f:	
		writer= csv.writer(f)
		writer.writerow(["이름","출장","교체(in)","교체(out)","교체(합)","GL(전)","GL(후)","GL(연)","GL(합)","AS","GK","CK","FC","OC","ST","PK_득","PK_실","PK%", "경고","퇴장","실점","자책"])
		out=[]
		for i in range(len(td_list)):
			if i is not 0 and i%22 == 0:
				writer.writerow(out)
				out=[]
			out.append(td_list[i].text)
			

			
	year=year+1
