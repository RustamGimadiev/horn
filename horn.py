# -*- coding: utf-8 -*-
#! /usr/bin/python

from io import StringIO
from lxml import etree
from multiprocessing import Process, Queue

import time
import requests
import hashlib
import json
import hornDB as db


	
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
	res = requests.get('https://www.instagram.com/%s/?__a=1' % obj.name)
	text = json.loads(res.text)
	latestId = text['user']['media']['nodes'][0]['code']
	result = msg % latestId
	return result

class Horn(Process):
	def __init__(self):
		self.toNotify = Queue()
		super(Horn, self).__init__()

	def run(self):
		YOUTUBE = db.ResourceSources.get(name='youtube')
		INSTAGRAM = db.ResourceSources.get(name='instagram')
		while True:
			rows = list(db.Resource.select())
			for r in rows:
				if r.source == YOUTUBE:
					m = getYouTubeLatest(r)
	                	        self.check(r, m)
				elif r.source == INSTAGRAM:
					m = getInstagramLatest(r)
					self.check(r, m)
				else:
					print "Unknown source for object: %s" % str(obj.source)

	def check(self, resource, message):
		updates = db.Update.select().where(db.Update.resource==resource)
		if not len(updates):
			update = db.Update.create(message=message, resource=resource)
                        self.toNotify.put((update.message, update.resource))
		else:
			update = updates[0]
		if update.message != message:
			u = db.Update.update(message=message).where(db.Update.resource==resource)
			u.execute()
			self.toNotify.put((update.message, update.resource))

	def getQueue(self):
		return self.toNotify

if  __name__ == "__main__":
	h = Horn()
	h.daemon = True
	h.start()
	h.join()
