import peewee as db
import time
import datetime

DB = db.SqliteDatabase('BotDataBase.sqlite')
DB.connect()

class BaseModel(db.Model):
    class Meta:
        database = DB

class Chat(BaseModel):
    id       = db.PrimaryKeyField()
    cID       = db.IntegerField(null=False)
    
    ChatName = db.TextField()

    MaxViewStat = db.IntegerField(null=False, default=15)


    class Meta:
        table_name = "Chat"

class User(BaseModel):
    
    # Base variables

    id      = db.PrimaryKeyField()
    chat_id    = db.ForeignKeyField(Chat)
    TgID    = db.IntegerField(null=False)
    FrstName= db.TextField(null=False)
    UsrStat = db.TextField(null=False,      default="user")
    UserName= db.TextField()
    lstup   = db.DateTimeField(null=False,   default=datetime.datetime.now())
    
    # Words counter

    wD      = db.IntegerField(null=False,   default=0) # Words per day
    bD      = db.IntegerField(null=False,   default=0) # Bad words per day

    wA      = db.IntegerField(null=False,   default=0) # Words in all
    bA      = db.IntegerField(null=False,   default=0) # Bad words in all

    dickl   = db.IntegerField()
    dicku   = db.DateField()

    class Meta:
        table_name = "Users"

class Married(BaseModel):

    id       = db.PrimaryKeyField()
    
    Usr1     = db.ForeignKeyField(User)
    Usr2     = db.ForeignKeyField(User)
    
    Time     = db.DateField(null=False)
    
    chat_id     = db.ForeignKeyField(Chat, null=False)

    class Meta:
        table_name = "Married"

class WordsPerDay(BaseModel):

    chat_id       = db.PrimaryKeyField()

    Usr      = db.ForeignKeyField(User)
    chat_id     = db.ForeignKeyField(Chat)

    Day      = db.DateField(null=False)

    Words    = db.IntegerField(null=False)
    BadWords = db.IntegerField(null=False)

    class Meta:
        table_name = "WordsPerDay"
            
if DB.table_exists("Chat") is not True:
    Chat.create_table()
if DB.table_exists("Users") is not True:
    User.create_table()
if DB.table_exists("Married") is not True:
    Married.create_table()
if DB.table_exists("WordsPerDay") is not True:
    WordsPerDay.create_table()