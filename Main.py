# Library

import os
import re
import time
import datetime
import wikipedia
import soundfile as sf
import speech_recognition as sr
from Func import *
from random import choice
from Models import User, Married
from PIL import Image, ImageDraw, ImageFont
from aiogram import Bot, Dispatcher, executor, types

# Config

try:
    import config
except Exception:
    print("You have not created a configuration file, create a config.py file and add the TOKEN variable there with the access token to the telegram bot api")
    quit()

# Bot

bot = Bot(config.TOKEN)
dp = Dispatcher(bot)

# Wikipedia settings

wikipedia.set_lang("ru")
r   = sr.Recognizer()

@dp.message_handler(content_types='any')
async def TextMessageProc(msg: types.Message):

    # Get User from database

    DBusr = User.get_or_none(User.TgID == msg.from_user.id, User.ChatID == msg.chat.id)
    
    msgTime = time.time()
    print(DBusr)
    if DBusr is None:
        DBusr = User(ChatID=msg.chat.id, TgID=msg["from"]["id"], UserName=msg["from"]["username"], FrstName=msg["from"]["first_name"], lstup=time.time())
        DBusr.save()
    
    DBusr = User.get_or_none(User.TgID == msg["from"]["id"], User.ChatID == msg.chat.id)

    nowUpdate = datetime.date.today()
    lstUpdate = DBusr.lstup

    if msg.content_type == 'voice':
        nowTime = time.time()
        await msg.voice.download(f"AudioFile/{nowTime}.ogg")
        text = SoundProc(f"AudioFile/{nowTime}.ogg")
        await bot.send_message(msg.chat.id, text)
    else:
        text = msg.text if msg.content_type == 'text' else msg.caption
    
    wrds = BadWordsCount(text)

    DBusr.bD += wrds[0]
    DBusr.wD += wrds[1]

    DBusr.bA += wrds[0]
    DBusr.wA += wrds[1]

    DBusr.lstup = nowUpdate
    
    if nowUpdate.day - lstUpdate.day != 0:
        UpdateWords = WordsPerDay(ChatID=msg.chat.id, Usr=DBusr, Day=DBusr.lstup, Words=DBusr.wD, BadWords=DBusr.bD)
        UpdateWords.save()
        DBusr.wD = 0
        DBusr.bD = 0

    DBusr.save()
    
    if len(text) != 0:

        if text == "/help@StatChat01bot":
            helpMessage = open("Help.txt", "r").read()
            await bot.send_message(msg.chat.id, helpMessage)
        elif text == "/start":
            await bot.reply("Для полноценной работы добавтье этого бота в группу и разрешите доступ к сообщениям")


        if re.match(r"бот|скайнет|бомж", text.lower()) is not None:
            text = "".join(re.split(r"бот|скайнет|бомж", text.lower(), maxsplit=1)).strip()

            print(text)

            if re.match(r'(расскажи|что(\sты\s|\s)знаешь) (о|про)\s', text) is not None:

                print("\n#--------Тырим вики-------------------------------------------------------\n")

                resp = wikipedia.search(re.split(r'(расскажи|что(\sты\s|\s)знаешь) (о|про)\s', text.lower(), maxsplit=1)[-1])
                if resp == []:
                    await bot.send_message(msg.chat.id, "Либо я тупой, а я не тупой, либо ты чёто не то спрашиваешь")
                else:
                    await bot.send_message(msg.chat.id, wikipedia.summary(resp[0]))

                print("\n#--------------------------------------------------------------------------\n")

            elif re.match(r"(пэсюн|хуй)", text) is not None:

                print("\n#--------Выростить писюн--------------------------------------------------\n")

                ri = choice([-5,-4,-3,-2,-1, 1, 2, 3, 4, 5 , 6, 7, 8, 9, 10])
                recent_time = datetime.time(hour=23-datetime.datetime.now().hour, minute=60-datetime.datetime.now().minute)
                if DBusr.dicku != datetime.date.today():


                    if DBusr.dickl is None:
                        ri = choice([1, 2, 3, 4, 5 , 6, 7, 8, 9, 10])
                        await msg.reply(f"{ DBusr.FrstName }, добро пожаловать в игру пэсюн!\nТвой песюн уже вырос на { ri } см.\nПродолжай играть через { recent_time.hour } ч. и { recent_time.minute } мин.\nХорошего дня)")
                        DBusr.dickl = 0
                    else:
                        if ri > 0:
                            await msg.reply(f"{ DBusr.FrstName }, твой песюн вырос на { ri } см.\nПродолжай играть через { recent_time.hour } ч. и { recent_time.minute } мин.\nХорошего дня)")
                        else:
                            await msg.reply(f"{ DBusr.FrstName }, твой песюн уменьшился на { abs(ri) } см.\nПродолжай играть через { recent_time.hour } ч. и { recent_time.minute } мин.\nХай щастыть наступного разу)")
                    DBusr.dicku = datetime.date.today()
                    DBusr.dickl += ri
                else:
                    await msg.reply(f"{ DBusr.FrstName }, ты уже сегодня играл, жду тебя через { recent_time.hour } ч. и { recent_time.minute } мин.\nХорошего дня)")

                DBusr.save()

                print("\n#--------------------------------------------------------------------------\n")

            elif re.match(r"(пэсюны|хуи)", text) is not None:

                print("\n#----------Список писюнов-------------------------------------------------\n")

                users = User.select().where(User.ChatID == msg.chat.id).order_by(User.dickl)
                p = 1
                txt = "Топ пэсюнов в чате:\n"
                for i in users[::-1]:
                    if i.dickl is not None:
                        txt += f"{p}. <a href='tg://user?id={ i.TgID }'>{i.FrstName}</a> - {i.dickl} см.\n"
                        p += 1
                await bot.send_message(msg.chat.id, txt, parse_mode=types.ParseMode.HTML)

                print("\n#--------------------------------------------------------------------------\n")

            elif re.match(r"(докладывай|загрузка)", text) is not None:
                
                print("\n#----------Загрузка пк-----------------------------------------------------\n")

                if os.name == "posix":
                    await bot.send_message(msg.chat.id, f"Загрузка CPU: {CPULoad()}%\nЗагрузка RAM: { RAMLoad() }")
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
                await bot.send_photo(chat_id=msg.chat.id, photo=open(f'PhotoOut/{ t }-rzf.jpg', 'rb'))

                print("\n#--------------------------------------------------------------------------\n")

            elif re.search(r"стата|статистика", text) is not None and re.search(r"моя", text) is not None:
                
                print("\n#----------Статистика------------------------------------------------------\n")

                """

                if re.search(r"месяц", text) is not None:
                    await bot.send_message(msg.chat.id, f"{ DBusr.FrstName }, за месяц ты сказал(-а) {    DBusr.wM } слов(матерных кста { DBusr.bM }).")
                elif re.search(r"неделю", text) is not None:
                    await bot.send_message(msg.chat.id, f"{ DBusr.FrstName }, за неделю ты сказал(-а) {   DBusr.wW } слов(матерных кста { DBusr.bW }).")
                elif re.search(r"день", text) is not None:
                    await bot.send_message(msg.chat.id, f"{ DBusr.FrstName }, за день ты сказал(-а) {     DBusr.wD } слов(матерных кста { DBusr.bD }).")
                else:
                    await bot.send_message(msg.chat.id, f"{ DBusr.FrstName }, за всё время ты сказал(-а) {DBusr.wA } слов(матерных кста { DBusr.bA }).")
            
                """

                print("\n#--------------------------------------------------------------------------\n")

            elif re.match(r"стата|статистика", text) is not None:

                print("\n#--------------Статистика чата----------------------------------------------\n")

                """

                f = []
                ft = ""
                if   text.lower().find("месяц")     != -1:
                    f = User.wM
                    ft = "месяц"
                elif text.lower().find("неделю")    != -1:
                    f = User.wW
                    ft = "неделю"
                elif text.lower().find("день")      != -1:
                    f = User.wD
                    ft = "день"
                else:
                    f = User.wA
                    ft = "всё время"

                users = User.select().where(User.ChatID == msg.chat.id).order_by(f)

                p = 1

                txt = f"Топ болтунов в чате за {ft}:\n"

                for i in users[::-1]:
                    txt += f"{p}. <a href='tg://user?id={ i.TgID }'>{i.FrstName}</a> - "
                    if text.lower().find("месяц") != -1:
                        txt += str(i.wM)
                    elif text.lower().find("неделю") != -1:
                        txt += str(i.wW)
                    elif text.lower().find("день") != -1:
                        txt += str(i.wD)
                    else:
                        txt += str(i.wA)
                    txt += f" слов.\n"
                    p += 1

                await bot.send_message(msg.chat.id, txt, parse_mode=types.ParseMode.HTML)
                
                """

                print("\n#--------------------------------------------------------------------------\n")

            elif re.match(r"общий сбор|собрать народ", text) is not None:

                print("\n#-------------Общий сбор--------------------------------------------------\n")

                users = User.select().where(User.ChatID == msg.chat.id)
                t = f"Общий сбор! Он был объявлен <a href='tg://user?id={ DBusr.TgID }'>{ DBusr.FrstName}</a>. Если вас разбудили\nсори"
                for i in users:
                    t += f"<a href='tg://user?id={ i.TgID }'>&#160</a>"
                await bot.send_message(msg.chat.id, t, parse_mode=types.ParseMode.HTML) 

                print("\n#--------------------------------------------------------------------------\n")

            elif re.match(r"браки", text) is not None:
                
                print("\n#--------Вывод списка браков-----------------------------------------------\n")
                
                Mar = Married.select().where(Married.ChatID == msg.chat.id)
                for i in Mar:
                    print(i)
                t = "💍 БРАКИ ЭТОЙ БЕСЕДЫ\n\n"
                p = 1
                if Mar != []:
                    for i in Mar:
                        q = datetime.date.today() - i.Time
                        t += f"{p}. <a href='tg://user?id={ i.Usr1.TgID }'>{ i.Usr1.FrstName }</a> + <a href='tg://user?id={ i.Usr2.TgID }'>{ i.Usr2.FrstName }</a>({ q.days // 30 } м. { q.days } дн.)\n" 
                        p += 1
                t+="\n💬 Чтобы вступить в брак с участником беседы, введите команду \"бот брак @ссылка\""
                await msg.reply(t, parse_mode=types.ParseMode.HTML)
                
                print("\n#--------------------------------------------------------------------------\n")


            elif re.match(r"брак|свадьба", text) is not None:


                print("\n#-------------------Предложение руки и сердца------------------------------\n")


                if get_marry(DBusr, msg.chat.id) is not None:
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
                        users = User.get_or_none(User.ChatID == msg.chat.id, User.UserName == username)
                        if users == None:
                            await msg.reply("Мм... хто цэ?")
                        else:
                            sr = get_marry(users, msg.chat.id)
                            if sr is None:
                                BtnYes = types.InlineKeyboardButton('Принять', callback_data=f'marry|{msg["from"]["username"]}|{username}')
                                BtnNo  = types.InlineKeyboardButton('Отклонить', callback_data=f'marryno|{msg["from"]["username"]}|{username}')
                                MarryKB =types.InlineKeyboardMarkup(row_width=2).row(BtnYes, BtnNo)
                                await msg.reply(f"<a href='tg://user?id={ users.TgID }'>{users.FrstName}</a>, согласен(а) ли ты заключить брак с {DBusr.FrstName}?", reply_markup=MarryKB, parse_mode=types.ParseMode.HTML)
                            else:
                                await msg.reply("Этот человек уже состоит в браке")

                print("\n#--------------------------------------------------------------------------\n")

            elif re.match(r"развод", text) is not None:

                print("\n#--------------------------Развод-------------------------------------------\n")

                marry = get_marry(DBusr, msg.chat.id)
                if marry is not None:
                    await msg.reply(f"<a href='tg://user?id={ DBusr.TgID }'>{DBusr.FrstName}</a>, вы рассторгли свой брак, который продлился { marry.Time.days } дней.", parse_mode=types.ParseMode.HTML)
                    marry.delete_instance()
                else:
                    await msg.reply("С кем разводиться собрался(-ась)?")
            elif re.match(r"мой брак", text) is not None:

                print("\n#----------------------Информация о браке------------------------------------\n")

                marry = get_marry(DBusr, msg.chat.id)

                if marry is None:
                    await bot.reply("Ты не состоишь в браке")
                else:
                    await bot.send_photo(msg.chat.id, photo=open(f"Cert/Marry{marry.id}.jpg", "rb"))


@dp.callback_query_handler()
async def process_callback_kb1btn1(callback_query: types.CallbackQuery):
    cbqr = callback_query
    print(cbqr)
    data = cbqr.data.split("|")
    
    UserFrom = cbqr["from"]["username"]
    DBusr = User.get(User.UserName == UserFrom, User.ChatID == cbqr.message.chat.id)
    
    if data[0] == "marry" and UserFrom == data[2]:
        if get_marry(DBusr, cbqr.message.chat.id) is None:
            userWith = User.get(User.UserName == data[1], User.ChatID == cbqr.message.chat.id)
            Marry = Married(Usr1=DBusr, Usr2=userWith, Time=datetime.date.today(), ChatID=cbqr.message.chat.id)
            Marry.save()
            createCert(DBusr.FrstName, userWith.FrstName, Marry.Time, Marry.id)
            await bot.send_photo(cbqr.message.chat.id, photo=open(f"Cert/Marry{Marry.id}.jpg", "rb"), caption="Поздравим же новоиспечённую пару с началом их супружеской жизни!!!")
            
            await bot.delete_message(cbqr.message.chat.id, cbqr.message.message_id)

    elif data[0] == "marryno" and UserFrom == data[2]:
        await bot.send_message(cbqr.message.chat.id, f"@{data[1]}, ну, не судьба, повезёт в другой раз(")
        await bot.delete_message(cbqr.message.chat.id, cbqr.message.message_id)

executor.start_polling(dp)
