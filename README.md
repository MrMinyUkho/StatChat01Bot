# Как запустить бота

Для запуска установите библиотеки из файла `requirements.txt` и запустите файл `init.sh`

В файле `config.py` укажите токен вашего бота:

```Python
TOKEN = "Токен вашего бота"
```
И укажите ключ к API random.org

```Python
RANDOM_KEY = "API ключ"
```

И зпустите бота командой
```
python Main.py		# или
python3 Main.py
```