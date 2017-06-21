# -*- coding: utf-8 -*-
#! /usr/bin/python

from io import StringIO
from lxml import etree
from multiprocessing import Process, Queue

import time
import requests
import re
import hashlib
import hornDB as db


def Check(key, value):
	return True

def Notify(queue):
	while True:
		msg = queue.get()
		channels = subscribesList.getChannels(msg[0])
		for channel in channels: 
			print "For channel %d: %s" %  (channel, msg[1])
	

def getYouTubeLatest(obj):
	msg = u'Новое видео: https://www.youtube.com%s'
	res = requests.get('https://www.youtube.com/%s/%s/videos' % (obj.type.name, obj.name))
	parser = etree.HTMLParser()
	tree = etree.parse(StringIO(res.text), parser)
	latest = tree.xpath("//div[@class='yt-lockup-content']/h3/a")[0]
	result = msg % (latest.get('href'))
	return result

def getInstagramLatest(obj):
	msg = u'Новая публикация: https://www.instagram.com/p/%s'
	res = requests.get('https://www.instagram.com/%s/' % obj.name)
	p = re.compile('"code[": ]+([^"]*)', re.IGNORECASE)
	latestId = p.search(res.text).groups()[0]
	result = msg % latestId
	return result

class Horn(Process):
	def __init__(self):
		self.toNotify = Queue()
		super(Horn, self).__init__()

	def run(self):
		i = 0
		YOUTUBE = db.ResourceSources.get(name='youtube')
		INSTAGRAM = db.ResourceSources.get(name='instagram')
		while True:
			print '%d iteration of Horn' % i
			i += 1
			for r in db.Resource.select():
				if r.source == YOUTUBE:
					m = getYouTubeLatest(r)
	                	        if Check(r, m):
						self.toNotify.put((r, m))
				elif r.source == INSTAGRAM:
					m = getInstagramLatest(r)
					if Check(r, m):
						self.toNotify.put((r, m))
				else:
					print "Unknown source for object: %s" % str(obj.source)
	
	def getQueue(self):
		return self.toNotify

if  __name__ == "__main__":
	h = Horn()
	h.daemon = True
	h.start()
	q = h.getQueue()
	n = Process(target=Notify, args=(q,))
	n.start()
	n.join()
	h.join()
