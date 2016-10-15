from bs4 import BeautifulSoup
import ctypes
import urllib.request
import urllib

import sys

from collections import Counter
import random
import webbrowser
from konlpy.tag import Hannanum
from lxml import html
import pytagcloud
import sys

libc = ctypes.cdll.LoadLibrary('libc.so.6')
res_init = libc.__res_init

if sys.version_info[0] >= 3:
    urlopen = urllib.request.urlopen
else:
    urlopen = urllib.urlopen

r =  lambda: random.randint(0,255)
color = lambda: (r(),r(),r())


def get_tag(text, ntags=50, multiplier=10):
    h = Hannanum()
    nouns = h.nouns(text)
    count = Counter(nouns)
    return [{ 'color' : color(), 'tag' : n, 'size': c*multiplier} for n,c in count.most_common(ntags)]


def draw_cloud(tags, filename, fontname='Noto Sans CJK', size=(800,600)):
    pytagcloud.create_tag_image(tags, filename, fontname=fontname, size=size)
    webbrowser.open(filename)



index = 1
my_list = []
s = ""
page =1
findMax=0
maxBoardNum = 0
subject_list = []
content_list = []

start = 185847
no  = start

while True:
	res_init()
	if index  == 0:
		break
        
    #Board List
	page_url = 'http://gall.dcinside.com/board/lists/?id=sweets&exception_mode=recommend&'+str(page)
	url_open = urllib.request.urlopen(page_url)
	soup = BeautifulSoup(url_open, 'html.parser', from_encoding = 'utf-8')
	notice_list = soup.findAll('td', attrs={'class':'t_notice'})
	hit_list = soup.findAll('td', attrs={'class':'t_hits'})
	sub_list = soup.select(".t_subject a")
	for i in range(len(sub_list)):
		subject_list.append(sub_list[i].text)

    #Content List
	page_url = 'http://gall.dcinside.com/board/view/?id=sweets&no='+str(no)+'&exception_mode=recommend'
	url_open = urllib.request.urlopen(page_url)
	soup = BeautifulSoup(url_open, 'html.parser', from_encoding = 'utf-8')
	p_list =  soup.select('.s_write p')

	for i in range(len(p_list)):
		content_list.append(p_list[i].text)

    #Find Maximum
	length = int(len(hit_list)/2)
	for i in range(length):
		try:
			tmp = int(hit_list[2*i].text)
			if findMax < tmp:
				maxBoardNum = int(notice_list[i].text)
				findMax = tmp
		except ValueError:
			print("not integer")
	index = index-1
	no = no-1
res_init()

#Maximum
page_url = 'http://gall.dcinside.com/board/view/?id=sweets&no='+str(maxBoardNum)
print(page_url)
url_open = urllib.request.urlopen(page_url)
soup = BeautifulSoup(url_open, 'html.parser', from_encoding = 'utf-8')
maxBoardContent = soup.select('.s_write')

out_list = []
for i in range(len(maxBoardContent)):
	out_list.append(maxBoardContent[i].text)
print(out_list)
s=""
for i in range(len(out_list)):
	s+=out_list[i]

tags = get_tag(s)
draw_cloud(tags, 'max.png')
print(tags)
with open('maximum.txt','w') as f:
	f.write('http://gall.dcinside.com/board/view/?id=sweets&no='+str(maxBoardNum))

with open('maximum.json','w') as f:
	f.write(str(tags))



#Content List
out_list = []
for i in range(len(content_list)):
	out_list.append(content_list[i])
s=""
for i in range(len(out_list)):
	s+=out_list[i]

tags = get_tag(s)
print('content_list')
draw_cloud(tags, 'content_list.png')


#Subject List
out_list = []
for i in range(len(subject_list)):
	out_list.append(subject_list[i])
s=""
for i in range(len(out_list)):
	s+=out_list[i]
tags = get_tag(s)

print('subject_list')
print(tags)
draw_cloud(tags, 'subject_list.png')
