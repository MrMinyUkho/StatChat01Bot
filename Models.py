import peewee as db
import time
import datetime

DB = db.SqliteDatabase('BotDataBase.sqlite')
DB.connect()

class BaseModel(db.Model):
    class Meta:
        database = DB

class User(BaseModel):
    
    # Base variables

    id      = db.PrimaryKeyField()
    ChatID  = db.IntegerField(null=False)
    TgID    = db.IntegerField(null=False)
    FrstName= db.TextField(null=False)
    UsrStat = db.TextField(null=False,      default="user")
    UserName= db.TextField()
    lstup   = db.DateTimeField(null=False,   default=datetime.datetime.now())

    # Mute (Not used)

    IsMuted = db.IntegerField(null=False,   default=0)
    MuteTime= db.IntegerField(null=False,   default=0)
    
    # Words counter

    wD      = db.IntegerField(null=False,   default=0) # Words per day
    bD      = db.IntegerField(null=False,   default=0) # Bad words per day

    wA      = db.IntegerField(null=False,   default=0) # Words in all
    bA      = db.IntegerField(null=False,   default=0) # Bad words in all

    dickl   = db.IntegerField()
    dicku   = db.IntegerField()

    class Meta:
        table_name = "Users"

class Married(BaseModel):

    id       = db.PrimaryKeyField()
    
    Usr1     = db.ForeignKeyField(User)
    Usr2     = db.ForeignKeyField(User)
    
    Time     = db.DateField(null=False)
    
    ChatID   = db.IntegerField(null=False)

    class Meta:
        table_name = "Married"

class WordsPerDay(BaseModel):

    id       = db.PrimaryKeyField()

    Usr      = db.ForeignKeyField(User)
    ChatID   = db.IntegerField(null=False)

    Day      = db.DateField(null=False)

    Words    = db.IntegerField(null=False)
    BadWords = db.IntegerField(null=False)

    class Meta:
        table_name = "WordsPerDay"
            

if DB.table_exists("Users") is not True:
    User.create_table()
if DB.table_exists("Married") is not True:
    Married.create_table()
if DB.table_exists("WordsPerDay") is not True:
    WordsPerDay.create_table()