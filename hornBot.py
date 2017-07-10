#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import horn
from multiprocessing import Process, Queue
import hornDB as db
from urlparse import urlparse
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, Bot)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)

logging.basicConfig(format='%(asctime)s [%(name)s][%(levelname)s] %(message)s',
                    level=logging.INFO)
logging.getLogger("requests").setLevel(logging.WARNING)
logger = logging.getLogger('horn')

class NotSupported(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return self.value

def parseUrl(url):
	o = urlparse(url)
	source = str.replace(str(o.netloc),'www.','').split('.')[0]
	if 'youtube' in source:
		type, name = o.path.split('/')[1:3]
		return name, type, source 
	elif 'instagram' in source:
		name = o.path.split('/')[1]
		return name, 'user', source
	else:
		logger.warning('Unable to parse: %s' % url)
		raise NotSupported('Wrong source, please use youtube or instagram')

def list(bot, update):
	l = ''
	chat = db.Chat.get(cid=update.message.chat_id)
	subs = db.Subscription.get(chat=chat)
	for i, r in enumerate(db.Resource.select().join(db.Subscription).where(db.Subscription.chat == chat)):
		l = l + '\n%d) %s %s %s' % (i+1, r.source.name, r.type.name, r.name) 
	update.message.reply_text(l)

def unsub(bot, update):
	_chat = update.message.chat_id
	try:
		id = text.split()[1]
	except IndexError as e:
                print 'Error', e
                update.message.reply_text('Try again with: /unsub URL')

def sub(bot, update):
	_chat = update.message.chat_id
	url = None
	try:
		text = update.message.text
		url = text.split()[1]
		name, _type, _source = parseUrl(url)
		type = db.ResourceTypes.get(name=_type)
		source = db.ResourceSources.get(name=_source)
		chat = db.Chat.get(cid=_chat)
		resource, created  = db.Resource.get_or_create(name=name, type=type, source=source)
		db.Subscription.create(chat=chat, resource=resource)
	except IndexError as e:
		print 'Error', e
		update.message.reply_text('Try again with: /sub URL')
	except NotSupported as e:
		update.message.reply_text(str(e))
	except Exception as e:
		logger.error(str(e))

def start(bot, update):
	name = update.message.chat.title
	if name is None:
		name = update.message.chat.username
	try:
		db.Chat.create(cid=update.message.chat_id, name=name)
		update.message.reply_text('Thank you for registration')
	except db.IntegrityError as e:
		update.message.reply_text('You already registered')

def help(bot, update):
	update.message.reply_text('help!',reply_markup=ReplyKeyboardRemove())
	
def notifier(queue):
	bot = Bot('346099461:AAFEvtDIZ9tHpBeHeJZdhuXNzAh1IxG_Vow')
	while True:
		msg = queue.get()
		for s in db.Subscription.select().where(db.Subscription.resource==msg[1]):
			bot.send_message(s.chat.cid, msg[0])

def updater():
	updater = Updater('346099461:AAFEvtDIZ9tHpBeHeJZdhuXNzAh1IxG_Vow')
	dp = updater.dispatcher
	conv_handler = ConversationHandler(
        	entry_points = [CommandHandler('start', start),CommandHandler('help', help), CommandHandler('sub', sub),CommandHandler('list', list),CommandHandler('unsub', unsub)],
        	states = {},
		fallbacks = []
	)
	dp.add_handler(conv_handler)
	updater.start_polling()
	updater.idle()

if __name__ == '__main__':
	h = horn.Horn()
        h.daemon = True
        h.start()
        q = h.getQueue()
	u = Process(target=updater)
        u.start()
	n = Process(target=notifier, args=(q,))
        n.start()
        n.join()
        u.join()
	h.join()

	main()
