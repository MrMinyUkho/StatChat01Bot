import os
import time
import soundfile as sf
import speech_recognition as sr
from PIL import Image, ImageDraw, ImageFont

r   = sr.Recognizer()

def BadWordsCount(text):
    badW    = ['бля', "пидор", "хуй", "хуё", "еба", "еби", "хуя", "хули", "хуи", "пизда", "пезд", "пизд", "ёбн", "еблан", "ебей"]
    
    b = 0
    if text is not None:
        for word in text.split():
            for j in badW:
                if j in word:
                    b = b + 1
                    break
        
        return [b, len(text.split())]
    else:
        return [0, 0]

def ImgProc(pathfrom, pathto, text):
    ts      = 90
    font    = ImageFont.truetype(font="times-new-roman.ttf", size=ts, index=0, encoding='UTF-8', layout_engine=None)
    oi        = Image.open(pathfrom)
    oi        = oi.resize((800, 800))
    brd        = Image.open('Border.jpg')
    brd.paste(oi, (50, 20))
    W, H    = 900, 120
    draw    = ImageDraw.Draw(brd)
    w, h    = draw.textsize(text, font=font)
    while w > W-50 and h > 5:
        ts-=2
        font = ImageFont.truetype(font="times-new-roman.ttf", size=ts, index=0, encoding='UTF-8', layout_engine=None)
        w, h    = draw.textsize(text, font=font)
    draw.text(((W-w)/2,820+(H-h)/2), text, fill="white", font=font)
    brd.save(pathto)

def SoundProc(pathfrom):
    t = ""
    try:
        data, samplerate = sf.read(pathfrom)
        sf.write(f"{pathfrom[:-4]}.wav", data, samplerate)
        os.remove(pathfrom)
        with sr.AudioFile(f"{pathfrom[:-4]}.wav") as source:
            audio_text = r.listen(source)
            try:
                t = r.recognize_google(audio_text, language="ru-RU")
            except Exception as e:
                print(e)
    except Exception as e:
        print(e)

    return t

def CPULoad():

    qwe = 0
    ewq = 0
    avg = 0      

    with open("/proc/stat") as st:
        proctimes = st.readline().split()
        for i in proctimes[1:]:
            qwe += int(i)
        avg -= int(proctimes[4])
    
    time.sleep(0.1)
    
    with open("/proc/stat") as st:
        proctimes = st.readline().split()
        for i in proctimes[1:]:
            ewq += int(i)
        avg += int(proctimes[4])

    return int((1 - avg / (ewq - qwe)) * 100) 

def RAMLoad():
    with open("/proc/meminfo") as st:
        Total = str(int(st.readline().split()[1])//1024) 
        Used  = str(int(Total)-int(st.readline().split()[1])//1024)

        return str(Used + "MB/" + Total + "MB")

def get_marry(Usr, chat):
    a = Married.get_or_none(Married.Usr1 == Usr.id, Married.ChatID==chat)
    b = Married.get_or_none(Married.Usr2 == Usr.id, Married.ChatID==chat)


    if a is not None:
        print(a)
        return a
    elif b is not None:
        print(b)
        return b
    else:
        return None

def createCert(Name1, Name2, date, marryID):
    print(Name1, Name2)
    font = ImageFont.truetype(font="times-new-roman.ttf", size=40, index=0, encoding='UTF-8', layout_engine=None)
    CertBase = Image.open("CertBase.jpg")

    draw = ImageDraw.Draw(CertBase)

    draw.text((360, 270), str(Name1), fill="white", anchor="mm", font=font)
    draw.text((360, 395), str(Name2), fill="white", anchor="mm", font=font)
    draw.text((590, 520), str(date.day)+" "+str(date.month)+" "+str(date.year), fill="white", anchor="mm", font=font)
    CertBase.save(f"Cert/Marry{marryID}.jpg")
