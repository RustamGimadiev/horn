from peewee import *


DATABASE = 'horn'
database = SqliteDatabase(DATABASE)

class BaseModel(Model):
	class Meta:
		database = database

class Chat(BaseModel):
	cid = IntegerField(unique=True)
	name = TextField()

class ResourceTypes(BaseModel):
	name = TextField(unique=True)

class ResourceSources(BaseModel):
	name = TextField(unique=True)

class Resource(BaseModel):
	name = TextField()
	type = ForeignKeyField(ResourceTypes)
	source = ForeignKeyField(ResourceSources)

class Subscription(BaseModel):
	chat = ForeignKeyField(Chat)
	resource = ForeignKeyField(Resource)
	class Meta:
		primary_key = CompositeKey('chat', 'resource')

class Update(BaseModel):
	message = TextField()
	resource = ForeignKeyField(Resource)

def init(db):
	db.init(DATABASE)
	db.connect()
	if not Chat.table_exists():
		Chat.create_table()
	if not ResourceTypes.table_exists():
		ResourceTypes.create_table()
		ResourceTypes.create(name='user')
		ResourceTypes.create(name='channel')
	if not ResourceSources.table_exists():
		ResourceSources.create_table()
		ResourceSources.create(name='youtube')
		ResourceSources.create(name='instagram')
	if not Resource.table_exists():
		Resource.create_table()
	if not Subscription.table_exists():
		Subscription.create_table()
	if not Update.table_exists():
		Update.create_table() 

init(database)
