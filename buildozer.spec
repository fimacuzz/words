[app]

# Название приложения
title = Словарный диктант

# Имя пакета (должно быть уникальным)
package.name = vocabdictation

# Доменное имя (обратный формат)
package.domain = ru.example

# Путь к исходникам
source.dir = .

# Основной файл приложения
source.include_exts = py,png,ttf,json,mp3
main.py = main.py

# Версия Android API
android.api = 34

# Минимальная версия Android
android.minapi = 21

# Целевая версия Android
android.ndk = 23b

# Разрешения
android.permissions = INTERNET

# Ориентация экрана
orientation = portrait

# Версия приложения
version = 1.0

# Требования
requirements =
    python3,
    kivy==2.3.0,
    kivymd==1.2.0,
    Levenshtein==0.25.1,
    android,
    openssl

# Пакеты для включения в специфические ОС
android.add_aars =
android.add_jars =
android.add_src =

# Дополнительные файлы
include.assets =
    words/
    *.png
    *.ttf
    wordlist.json

# Настройки выпуска
[buildozer]
log_level = 2
warn_on_root = 1