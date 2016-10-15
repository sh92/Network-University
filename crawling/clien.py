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

index = 0
my_list = []
s = ""
init_number = 934827
page =1
while True:
	if index  == 20:
		break
	no = init_number+index
	page_url = ' http://www.clien.net/cs2/bbs/board.php?bo_table=use&wr_id='+str(no)
	url_open = urllib.request.urlopen(page_url)
	soup = BeautifulSoup(url_open, 'html.parser', from_encoding = 'utf-8')
	p_list = soup.select('#writeContents')

	for i in range(0, len(p_list)):
    		my_list.append(p_list[i].text)
	index = index+1

for i in range(0, len(my_list)):
    s += my_list[i]
tags = get_tag(s)
print(tags)
draw_cloud(tags, 'clien.png')
