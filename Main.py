# Library

import os
import re
import time
import datetime
import wikipedia
import soundfile as sf
import matplotlib.pyplot as plt
import speech_recognition as sr
from Func import *
from random import choice
from Models import User, Married, WordsPerDay, Chat
from PIL import Image, ImageDraw, ImageFont
from aiogram import Bot, Dispatcher, executor, types

# Config

try:
    import config
except Exception:
    print("You have not created a configuration file, create a config.py file and add the TOKEN variable there with the access token to the telegram bot api")
    quit()

# Bot

bot = Bot(config.TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

# Wikipedia settings

wikipedia.set_lang("ru")
r   = sr.Recognizer()

@dp.message_handler(content_types='any')
async def TextMessageProc(msg: types.Message):

    try:
        if config.S_MSG == True:
            if msg.chat.id == config.myid:
                print(f"send to {config.chat}")
                await bot.send_message(config.chat, msg.text)
            if msg.chat.id == config.chat:
                print(f"send to {config.myid}")
                await bot.send_message(config.myid, msg.text)
    except BaseException:
        pass

    if msg.chat.id > 0:
        print(f"From user ID:{msg.chat.id}, UserName:{msg['from']['username']}")
    else:
        print(f"From chat ID:{msg.chat.id}, UserName:{msg['from']['username']}")

    DBchat = Chat.get_or_none(Chat.cID==msg.chat.id)
    if DBchat is None:
        DBchat = Chat(cID = msg.chat.id, ChatName=msg.chat.title)
        DBchat.save()


    DBusr = User.get_or_none(User.TgID == msg.from_user.id, User.chat_id == DBchat)
    if DBusr is None:
        DBusr = User(chat_id = DBchat, TgID=msg["from"]["id"], UserName=msg["from"]["username"], FrstName=msg["from"]["first_name"], lstup=datetime.date.today())
        DBusr.save()
    
    nowUpdate = datetime.date.today()
    lstUpdate = DBusr.lstup

    if msg.content_type == 'voice':
        nowTime = time.time()
        await msg.voice.download(f"AudioFile/{nowTime}.ogg")
        text = SoundProc(f"AudioFile/{nowTime}.ogg")
        if text != "":
            await bot.send_message(msg.chat.id, text)
    else:
        text = msg.text if msg.content_type == 'text' else msg.caption
    
    wrds = BadWordsCount(text)

    DBusr.bD += wrds[0]
    DBusr.wD += wrds[1]

    DBusr.bA += wrds[0]
    DBusr.wA += wrds[1]

    
    if nowUpdate.day - lstUpdate.day != 0:
        UpdateWords = WordsPerDay(chat_id=DBchat, Usr=DBusr, Day=lstUpdate, Words=DBusr.wD, BadWords=DBusr.bD)
        UpdateWords.save()
        DBusr.wD = 0
        DBusr.bD = 0

    DBusr.lstup = nowUpdate
    DBusr = UpdateUser(DBusr, msg)
    DBusr.save()
    
    if text is not None and len(text) != 0:

        if text == "/help@StatChat01bot":
            helpMessage = open("Help.txt", "r").read()
            await bot.send_message(DBchat.cID, helpMessage)
        elif text in ["/start", "/help"]:
            await msg.reply("Для полноценной работы добавтье этого бота в группу и разрешите доступ к сообщениям")

        if re.match(r"бот|скайнет|бомж", text.lower()) is not None:
            text = "".join(re.split(r"бот|скайнет|бомж", text.lower(), maxsplit=1)).strip()

            print(text)

            if re.match(r'(расскажи|что(\sты\s|\s)знаешь) (о|про)\s', text) is not None:

                print("\n#--------Тырим вики-------------------------------------------------------\n")

                resp = wikipedia.search(re.split(r'(расскажи|что(\sты\s|\s)знаешь) (о|про)\s', text.lower(), maxsplit=1)[-1])
                if resp == []:
                    await bot.send_message(DBchat.cID, "Либо я тупой, а я не тупой, либо ты чёто не то спрашиваешь")
                else:
                    await bot.send_message(DBchat.cID, wikipedia.summary(resp[0]))

                print("\n#--------------------------------------------------------------------------\n")

            elif re.match(r"(пэсюн|хуй)", text) is not None:

                print("\n#--------Выростить писюн--------------------------------------------------\n")

                ri = choice([-5,-4,-3,-2,-1, 1, 2, 3, 4, 5 , 6, 7, 8, 9, 10])
                recent_time = datetime.time(hour=23-datetime.datetime.now().hour, minute=59-datetime.datetime.now().minute)
                if DBusr.dicku != datetime.date.today():


                    if DBusr.dickl is None:
                        ri = choice([1, 2, 3, 4, 5 , 6, 7, 8, 9, 10])
                        await msg.reply(f"{ UserLink(DBusr) }, добро пожаловать в игру пэсюн!\nТвой песюн уже вырос на { ri } см.\nПродолжай играть через { recent_time.hour } ч. и { recent_time.minute } мин.\nХорошего дня)")
                        DBusr.dickl = 0
                    else:
                        if ri > 0:
                            await msg.reply(f"{ UserLink(DBusr) }, твой песюн вырос на { ri } см.\nПродолжай играть через { recent_time.hour } ч. и { recent_time.minute } мин.\nХорошего дня)")
                        else:
                            await msg.reply(f"{ UserLink(DBusr) }, твой песюн уменьшился на { abs(ri) } см.\nПродолжай играть через { recent_time.hour } ч. и { recent_time.minute } мин.\nХай щастыть наступного разу)")
                    DBusr.dicku = datetime.date.today()
                    DBusr.dickl += ri
                else:
                    await msg.reply(f"{ UserLink(DBusr) }, ты уже сегодня играл, жду тебя через { recent_time.hour } ч. и { recent_time.minute } мин.\nХорошего дня)")

                DBusr.save()

                print("\n#--------------------------------------------------------------------------\n")

            elif re.match(r"(пэсюны|хуи)", text) is not None:

                print("\n#----------Список писюнов-------------------------------------------------\n")

                users = User.select().where(User.chat_id == DBchat).order_by(User.dickl)
                p = 1
                txt = "Топ пэсюнов в чате:\n"
                for i in users[::-1]:
                    if i.dickl is not None:
                        txt += f"{p}. { UserLink(i) } - {i.dickl} см.\n"
                        p += 1
                await bot.send_message(DBchat.cID, txt)

                print("\n#--------------------------------------------------------------------------\n")

            elif re.match(r"(докладывай|загрузка)", text) is not None:
                
                print("\n#----------Загрузка пк-----------------------------------------------------\n")

                if os.name == "posix":
                    await bot.send_message(DBchat.cID, f"Загрузка CPU: {CPULoad()}%\nЗагрузка RAM: { RAMLoad() }")
                else:
                    await bot.reply("Система на которой запущен бот не является GNU/Linux выполнение команды невозможно(")

                print("\n#--------------------------------------------------------------------------\n")

            elif re.match(r"фото|ржака|мем", text) is not None:

                print("\n#---------Ржакамем---------------------------------------------------------\n")

                t  = time.time()
                await msg.delete()
                if msg.content_type == "text" and msg.reply_to_message.photo is not None:
                    await msg.reply_to_message.photo[-1].download(f"Photo/{ t }-rz.jpg")
                elif msg.content_type == "photo":
                    await msg.photo[-1].download(f"Photo/{ t }-rz.jpg")

                print(("".join(re.split(r"фото|ржака|мем", text)).strip()))

                ImgProc(f"Photo/{ t }-rz.jpg", f"PhotoOut/{ t }-rzf.jpg", "".join(re.split(r"фото|ржака|мем", text)).strip())
                await bot.send_photo(chat_id=DBchat.cID, photo=open(f'PhotoOut/{ t }-rzf.jpg', 'rb'))

                print("\n#--------------------------------------------------------------------------\n")

            elif re.search(r"стата|статистика", text) is not None and re.search(r"моя", text) is not None:
                
                print("\n#----------Статистика------------------------------------------------------\n")

                tm = time.time()

                Stat = WordsPerDay.select().where(WordsPerDay.chat_id==DBchat, WordsPerDay.Usr==DBusr).order_by(WordsPerDay.Day)

                YplotW = []
                YplotB = []
                Xplot  = []

                for i in Stat:
                    YplotW.append(i.Words)
                    YplotB.append(i.BadWords)
                    Xplot.append(f"{i.Day.day},{str(i.Day.month)}")

                print(YplotW, YplotB, Xplot)

                plt.clf()
                plt.plot(Xplot, YplotB, Xplot, YplotW)
                plt.ylabel("Количевство слов")
                plt.xlabel("Время")
                plt.savefig(f"StatPlot/StPl{tm}.jpg")

                WordsM = 0
                WordsW = 0
                BadWordsM = 0
                BadWordsW = 0

                p = 0
                l = min(len(Xplot), 30)

                for i in range(l):
                    
                    if i < 6:
                        WordsW += YplotW[i]
                        BadWordsW += YplotB[i]
                    
                    WordsM += YplotW[i]
                    BadWordsM += YplotB[i]

                t = f"\
                Статистика пользователя { UserLink(DBusr) }\
                \nСлов за день: {DBusr.wD}, матов: {DBusr.bD}\
                \nСлов за неделю: { WordsW }, матов: { BadWordsW }\
                \nСлов за месяц: { WordsM }, матов: { BadWordsM }\
                \nСлов за всё время: { DBusr.wA }, матов: { DBusr.bA }."

                await bot.send_photo(msg.chat.id, photo=open(f"StatPlot/StPl{tm}.jpg", "rb"), caption=t)

                print("\n#--------------------------------------------------------------------------\n")

            elif re.match(r"стата|статистика", text) is not None:

                print("\n#--------------Статистика чата----------------------------------------------\n")

                users = User.select().where(User.chat_id == DBchat).order_by(User.wA)

                txt = f"Топ болтунов в чате за всё время:\n"

                p = 1
                for i in users[::-1]:
                    txt += f"{p}. { UserLink(i) } - {i.wA} слов.\n"
                    p += 1

                await bot.send_message(DBchat.cID, txt)

                print("\n#--------------------------------------------------------------------------\n")

            elif re.match(r"общий сбор|собрать народ", text) is not None:

                print("\n#-------------Общий сбор--------------------------------------------------\n")

                users = User.select().where(User.chat_id == DBchat)
                t = f"Общий сбор! Он был объявлен <a href='tg://user?id={ DBusr.TgID }'>{ DBusr.FrstName}</a>. Если вас разбудили\nсори"
                for i in users:
                    t += f"{ UserLink(ID=i.TgID, Name='&#160') }"
                await bot.send_message(DBchat.cID, t) 

                print("\n#--------------------------------------------------------------------------\n")

            elif re.match(r"браки", text) is not None:
                
                print("\n#--------Вывод списка браков-----------------------------------------------\n")
                
                Mar = Married.select().where(Married.chat_id == DBchat)
                t = "💍 БРАКИ ЭТОЙ БЕСЕДЫ\n\n"
                p = 1
                if Mar != []:
                    for i in Mar:
                        q = datetime.date.today() - i.Time
                        print(datetime.date.today(), "-", i.Time, "=", q)
                        t += f"{p}. { UserLink(i.Usr1) } + { UserLink(i.Usr2) }({ q.days // 30 } м. { q.days % 30} дн.)\n" 
                        p += 1
                t+="\n💬 Чтобы вступить в брак с участником беседы, введите команду \"бот брак @ссылка\""
                await msg.reply(t)
                
                print("\n#--------------------------------------------------------------------------\n")


            elif re.match(r"брак|свадьба", text) is not None:


                print("\n#-------------------Предложение руки и сердца------------------------------\n")


                if get_marry(DBusr, DBchat) is not None:
                    await msg.reply("Мм... ты же уже в браке...")
                else:
                    text = msg.text.split()
                    username = ""
                    for i in text:
                        if i[0] == "@":
                            username = i[1:]
                    if username == "":
                        await msg.reply("Мм... а с кем свадьба?")
                    else:
                        users = User.get_or_none(User.chat_id == DBchat, User.UserName == username)
                        if users == None:
                            await msg.reply("Мм... хто цэ?")
                        else:
                            sr = get_marry(users, msg.chat.id)
                            if sr is None:
                                BtnYes = types.InlineKeyboardButton('Принять', callback_data=f'marry|{msg["from"]["username"]}|{username}')
                                BtnNo  = types.InlineKeyboardButton('Отклонить', callback_data=f'marryno|{msg["from"]["username"]}|{username}')
                                MarryKB =types.InlineKeyboardMarkup(row_width=2).row(BtnYes, BtnNo)
                                await msg.reply(f"{ UserLink(users) }, согласен(а) ли ты заключить брак с { UserLink(DBusr) }?", reply_markup=MarryKB)
                            else:
                                await msg.reply("Этот человек уже состоит в браке")

                print("\n#--------------------------------------------------------------------------\n")

            elif re.match(r"развод", text) is not None:

                print("\n#--------------------------Развод-------------------------------------------\n")

                marry = get_marry(DBusr, DBchat)
                if marry is not None:
                    await msg.reply(f"{ UserLink(DBusr) }, вы рассторгли свой брак, который продлился { marry.Time.days } дней.")
                    marry.delete_instance()
                else:
                    await msg.reply("С кем разводиться собрался(-ась)?")
            elif re.match(r"мой брак", text) is not None:

                print("\n#----------------------Информация о браке------------------------------------\n")

                marry = get_marry(DBusr, DBchat)

                if marry is None:
                    await msg.reply("Ты не состоишь в браке")
                else:
                    pho = ""
                    try:
                        pho = open(f"Cert/Marry{marry.id}.jpg", "rb")
                    except Exception as e:
                        createCert(marry.Usr2.FrstName, marry.Usr1.FrstName, marry.Time, marry.id)
                        pho = open(f"Cert/Marry{marry.id}.jpg", "rb")

                    await bot.send_photo(DBchat.cID, photo=pho)


@dp.callback_query_handler()
async def process_callback_kb1btn1(callback_query: types.CallbackQuery):
    cbqr = callback_query
    print(cbqr)
    data = cbqr.data.split("|")
    
    UserFrom = cbqr["from"]["username"]
    DBchat = Chat.get_or_none(Chat.cID==cbqr.message.chat.id)
    DBusr = User.get(User.UserName == UserFrom, User.chat_id == DBchat)

    
    if data[0] == "marry" and UserFrom == data[2]:
        if get_marry(DBusr, DBchat) is None:
            userWith = User.get(User.UserName == data[1], User.chat_id == DBchat)
            Marry = Married(Usr1=DBusr, Usr2=userWith, Time=datetime.date.today(), chat_id=DBchat)
            Marry.save()
            createCert(DBusr.FrstName, userWith.FrstName, Marry.Time, Marry.id)
            await bot.send_photo(DBchat.cID, photo=open(f"Cert/Marry{Marry.id}.jpg", "rb"), caption="Поздравим же новоиспечённую пару с началом их супружеской жизни!!!")
            
            await bot.delete_message(DBchat.cID, cbqr.message.message_id)

    elif data[0] == "marryno" and UserFrom == data[2]:
        await bot.send_message(cbqr.message.chat.id, f"@{data[1]}, ну, не судьба, повезёт в другой раз(")
        await bot.delete_message(cbqr.message.chat.id, cbqr.message.message_id)

executor.start_polling(dp)

#  250 W 5V