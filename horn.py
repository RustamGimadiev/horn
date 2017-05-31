# -*- coding: utf-8 -*-
#! /usr/bin/python

from io import StringIO
from lxml import etree
import requests
import re
import hashlib
import json
import Queue

YOUTUBE=1
INSTAGRAM=2

def Check(key, value):
	store = {}
	uniqe = False
	with open('localStore.json', 'r+') as file:
		try:
			store = json.load(file)
		except ValueError as e:
			print "Unable to parse file, countinue with empty store: " + str(e)
		try:
			if store[key] is not None:
				uniqe = ( store[key] != value )
				if uniqe:
					store[key] = value
		except KeyError as e:
			store[key] = value
		file.seek(0)	
		json.dump(store, file)
		file.close()
	return uniqe

def getSubs(id):
	return [1]

def Notify(queue):
	while not queue.empty():
		msg = queue.get()
		subs = getSubs(msg[0])
		for sub in subs: 
			print "For channel %d: %s" %  (sub, msg[1])
	

def GetMD5(string):
	return hashlib.md5(string).hexdigest()

class Object():
	def __init__(self, source=None, profile=None, type='user'):
		self.source = source
		self.profile = profile
		self.type = type

	def getId(self):
		return GetMD5('%d:%s' % (self.source, self.profile))

def getYouTubeLatest(obj):
	msg = u'Новое видео "%s": https://www.youtube.com%s'
	res = requests.get('https://www.youtube.com/%s/%s/videos' % (obj.type, obj.profile))
	parser = etree.HTMLParser()
	tree = etree.parse(StringIO(res.text), parser)
	latest = tree.xpath("//div[@class='yt-lockup-content']/h3/a")[0]
	result = msg % (latest.text, latest.get('href'))
	return result, GetMD5(result.encode('unicode-escape'))

def getInstagramLatest(obj):
	msg = u'Новая публикация "%s": https://www.instagram.com/p/%s'
	res = requests.get('https://www.instagram.com/%s/' % obj.profile)
	p = re.compile('"code[": ]+([^"]*)', re.IGNORECASE)
	latestId = p.search(res.text).groups()[0]
	res = requests.get('https://www.instagram.com/p/%s/' % latestId)
	p = re.compile('text[": ]+([^"]*)', re.IGNORECASE)
	latest = p.search(res.text).groups()[0]
	result = msg % (latest.decode('unicode-escape'), latestId)
	return result, GetMD5(result.encode('unicode-escape'))

def main():
	objects = [Object(YOUTUBE, 'UCEVNTzTFSGkZGTjVE9ipXpg', 'channel'), Object(YOUTUBE, 'Academeg', 'user'), Object(YOUTUBE, 'Academeg2ndCH', 'user'), Object(INSTAGRAM, 'Academeg')]
	toNotify = Queue.Queue()
	for obj in objects:
		id = obj.getId()
		if obj.source == YOUTUBE:
			res = getYouTubeLatest(obj)
                        if Check(id, res[1]):
				toNotify.put((id, res[0]))
		elif obj.source == INSTAGRAM:
			res = getInstagramLatest(obj)
			if Check(id, res[1]):
				toNotify.put((res[0]))
		else:
			print "Unknown source for object: %s" % str(obj.source)

	Notify(toNotify)

if  __name__ == "__main__":
	main()
