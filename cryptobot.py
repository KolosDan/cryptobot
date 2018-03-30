
# coding: utf-8

# In[1]:


import telebot
import signal
from backend import create_user,_update,create_ico,get_balance,change_lock,get_deposit_addr
from pymongo import MongoClient
import sys
from adminPanel import admin
import time
from telebot import types


# In[2]:


token = "564747088:AAEAP-YnUgtqDfo--lGZNi89VOGR_cWfyYE"
bot = telebot.TeleBot(token)
#url = "https://api.telegram.org/bot%s/"% token 
db = MongoClient('213.183.48.143').cryptobot


# In[3]:


@bot.message_handler(commands=['start'])
def start(message):
    create_user(message.from_user.id,message.from_user.username)
    keyboard = types.ReplyKeyboardMarkup()
    btn = types.InlineKeyboardButton(text="💼ICO клуб")
    btn1= types.InlineKeyboardButton(text="🔌Майнинг, оборудование")
    keyboard.row(btn,btn1)
    btn2= types.InlineKeyboardButton(text="📈Торговые рекомендации")
    btn3= types.InlineKeyboardButton(text="🗣Приватный чат экспертов")
    keyboard.row(btn2,btn3)
    btn4= types.InlineKeyboardButton(text="🎁Розыгрыш BTC")
    btn5= types.InlineKeyboardButton(text="📖База знаний")
    keyboard.row(btn4,btn5)
    btn6= types.InlineKeyboardButton(text="👨🏻‍💻Личный кабинет")
    btn7= types.InlineKeyboardButton(text="💵Покупка BTC")
    keyboard.row(btn6,btn7)
    bot.send_message(message.chat.id, "👋 Приветствуем, %s! В главном меню Вы можете выбрать то, что Вас интересует:" % message.from_user.first_name,reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text=="👨🏻‍💻Личный кабинет")
def cabinet(message):
    keybd = types.InlineKeyboardMarkup()
    data = db.user.find_one({"id":int(message.from_user.id)})
    if data['permissions']['is_admin'] == "true":
        admin_button = types.InlineKeyboardButton(text="Админка", callback_data=str(message.chat.id) + "_admin")
        keybd.row(admin_button)
    b = types.InlineKeyboardButton(text="💳 ETH кошелек", callback_data=str(message.chat.id) + "_eth")
    b1= types.InlineKeyboardButton(text="📨 EMAIL адрес", callback_data=str(message.chat.id) +"_email")
    b2= types.InlineKeyboardButton(text="📱 Номер телефона", callback_data=str(message.chat.id) +"_phone")
    b3= types.InlineKeyboardButton(text="🕓 История", callback_data=str(message.chat.id) +"_history")
    b4 = types.InlineKeyboardButton(text="💰 Пополнить баланс", callback_data=str(message.chat.id) + "_deposit")
    keybd.row(b,b1)
    keybd.row(b2,b3)
    keybd.row(b4)
    bot.send_message(message.chat.id, "👨🏻‍💻 Кабинет")
    bot.send_message(message.chat.id, "🔑 Вы не являетесь членом нашего закрытого сообщества Private Crypto.\nДля вас действует стандартная комиссия на ICO клуб.\nДля вас не действует скидка на оборудование для майнинга.\nДля вас не действует скидка на Приватный канал с торговыми рекомендациями.")
    bot.send_message(message.chat.id, "🆔 Ваш id клиента: %s" % data["id"])
    if data['eth_addr'] == None:
        bot.send_message(message.chat.id, "💳 У Вас нет ETH кошелька")
    else:
        bot.send_message(message.chat.id, "💳 Адрес Вашего ETH кошелька: %s" % data['eth_addr'])
    if data['email'] == None:
        bot.send_message(message.chat.id, "📨 У Вас не задан e-mail")
    else:
        bot.send_message(message.chat.id, "📨 Ваш e-mail: %s" % data['email'])
    if data['phone'] == None:
        bot.send_message(message.chat.id, "📱 У Вас не задан номер телефона",reply_markup=keybd)
    else:
        bot.send_message(message.chat.id, "📱 Ваш номер телефона: %s" % data['phone'],reply_markup=keybd)

@bot.message_handler(func=lambda message: message.text=="🗣Приватный чат экспертов")
def private(message):
    keybd = types.InlineKeyboardMarkup()
    b = types.InlineKeyboardButton(text="🔑 Получить доступ", callback_data=str(message.chat.id) + "_access")
    b1= types.InlineKeyboardButton(text="❓ Задать вопрос", callback_data=str(message.chat.id) +"_question")
    keybd.row(b,b1)
    bot.send_message(message.chat.id, "🗣Приватный чат экспертов")
    bot.send_message(message.chat.id, """⚜️ В нем собираются эксперты рынка, трейдеры с опытом и просто успешные инвесторы в криптовалюту.\nИмея доступ к чату, вы становитесь полноправным членом сообщества Private Crypto и имеете скидку на наши услуги:""")
    bot.send_message(message.chat.id, """✅ Комиссия за участие во всех проектах ICO клуба будет равна 3%\n✅ Скидка на подписку на канал с торговыми рекомендациями 50%\n✅ Скидка на оборудование для майнинга 5%""")
    bot.send_message(message.chat.id, """💵 Стоимость участия:\n1 месяц - 0.3 ETH\n3 месяца - 0.7 ETH\n1 год - 1.5 ETH\nНавсегда - 2.5 ETH""",reply_markup=keybd)
    
@bot.message_handler(func=lambda message: message.text=="💼ICO клуб")
def ICO(message):
    print(message)
    keyboard = types.ReplyKeyboardMarkup()
    btn = types.InlineKeyboardButton(text="🤝 Принять участие")
    btn1= types.InlineKeyboardButton(text="🏆 Преимущества клуба")
    keyboard.row(btn,btn1)
    btn2= types.InlineKeyboardButton(text="Вопросы и ответы")
    btn3= types.InlineKeyboardButton(text="📖База знаний ICO")
    keyboard.row(btn2,btn3)
    btn4= types.InlineKeyboardButton(text="🔙 Главное меню")
    keyboard.row(btn4)
    bot.send_message(message.chat.id, "💼ICO клуб",reply_markup=keyboard)
    bot.send_message(message.chat.id, "💼 ICO клуб это быстрый и удобный инструмент для совместных инвестиций в ICO.\nМы предлагаем интересные проекты, отобранные нашими аналитиками и участниками сообщества, на самых выгодных условиях.")
    bot.send_message(message.chat.id, "⚠️ Перед использованием бота рекомендуем ознакомиться с инструкцией и соглашением.")
    bot.send_message(message.chat.id, "🔑 Для доступа в приватный чат перейдите в 🗣 Приватный чат экспертов")
    
@bot.message_handler(func=lambda message: message.text=="🔙 Главное меню")
def startmenu(message):
    keyboard = types.ReplyKeyboardMarkup()
    btn = types.InlineKeyboardButton(text="💼ICO клуб")
    btn1= types.InlineKeyboardButton(text="🔌Майнинг, оборудование")
    keyboard.row(btn,btn1)
    btn2= types.InlineKeyboardButton(text="📈Торговые рекомендации")
    btn3= types.InlineKeyboardButton(text="🗣Приватный чат экспертов")
    keyboard.row(btn2,btn3)
    btn4= types.InlineKeyboardButton(text="🎁Розыгрыш BTC")
    btn5= types.InlineKeyboardButton(text="📖База знаний")
    keyboard.row(btn4,btn5)
    btn6= types.InlineKeyboardButton(text="👨🏻‍💻Личный кабинет")
    btn7= types.InlineKeyboardButton(text="💵Покупка BTC")
    keyboard.row(btn6,btn7)
    bot.send_message(message.chat.id, "Главное меню",reply_markup=keyboard)
    
@bot.message_handler(func=lambda message: message.text=="🔌Майнинг, оборудование")
def mining(message):
    bot.send_message(message.chat.id, "🔌Майнинг, оборудование")

@bot.message_handler(func=lambda message: message.text=="🎁Розыгрыш BTC")
def btc(message):
    bot.send_message(message.chat.id, "🎁Розыгрыш BTC")
    
@bot.message_handler(func=lambda message: message.text=="📱 Изменить номер телефона")
def phone(message):
    bot.send_message(message.chat.id, "Введите номер в формате +79000000000")
    bot.register_next_step_handler(message,phone_change)

def phone_change(message):
    if _update(message.from_user.id,"phone",message.text) != False:
        bot.send_message(message.chat.id, "Телефон успешно обновлен!")
    else:
        bot.send_message(message.chat.id, "Что-то пошло не так:(\nПроверьте правильность введенных данных")
        
@bot.message_handler(func=lambda message: message.text=="📨 Изменить Email")
def email(message):
    bot.send_message(message.chat.id, "Введите Email")
    bot.register_next_step_handler(message,email_change)

def email_change(message):
    if _update(message.from_user.id,"email",message.text) != False:
        bot.send_message(message.chat.id, "Email успешно обновлен!")
    else:
        bot.send_message(message.chat.id, "Что-то пошло не так:(\nПроверьте правильность введенных данных")
    
@bot.message_handler(func=lambda message: message.text=="💳 Изменить ETH кошелек")
def eth(message):
    bot.send_message(message.chat.id, "Введите ETH кошелек")
    bot.register_next_step_handler(message,wallet_change)
    
def wallet_change(message):
    if _update(message.from_user.id,"eth_addr",message.text) != False:
        bot.send_message(message.chat.id, "Кошелек успешно обновлен!")
    else:
        bot.send_message(message.chat.id, "Что-то пошло не так:(\nПроверьте правильность введенных данных")
    
@bot.message_handler(func=lambda message: message.text=="🤝 Принять участие")
def takepart(message):
    keyboard = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(text="Модель 🅰️", callback_data=str(message.chat.id) + "_modelA")
    btn1= types.InlineKeyboardButton(text="Модель 🅱️", callback_data=str(message.chat.id) +"_modelB")
    keyboard.row(btn,btn1)
    bot.send_message(message.chat.id, "У нас есть 2 формата участия в нашем ICO клубе:")
    bot.send_message(message.chat.id, "Модель 🅰️ – участие в пуле на конкретное заявленное ICO.\nВыбор проекта осуществляется всеми участниками из предложенных и отобранных нашей командой аналитиков.\nКомиссия клуба: 5-15%")
    bot.send_message(message.chat.id, "Комиссия клуба: 5-15%")
    bot.send_message(message.chat.id, "Модель 🅱️ – участие в 5 проектах на усмотрение клуба.\nУчастника не нужно заморачиваться и тратить свое время на выбор проектов, регистрации и прочее.\nНаша команда сделает это за вас. Проекты будут отобраны в течении 1-2 месяцев.\nКомиссия клуба: 12%")
    bot.send_message(message.chat.id, "Комиссия клуба: 12%")
    bot.send_message(message.chat.id, "🎁 Всем участникам ICO клуба дается доступ на 1 месяц к Приватному чату экспертов Private Crypto в подарок.")
    bot.send_message(message.chat.id, "Выбери свою модель участия:", reply_markup=keyboard)
    
@bot.message_handler(func=lambda message: message.text=="🏆 Преимущества клуба")
def advantages(message):
    bot.send_message(message.chat.id, """Участвуя с нами, вы получаете:
·         Бонус на токены до 70% (% бонуса зависит от проекта и количества привлеченных средств)
·         Отсутствие заморочек со всеми белыми списками, верификацией, отслеживанием времени участия
·         Возможность вложить большую сумму, потому что тенденция публичных распродаж – уменьшать индивидуальную капитализацию.
·         Доступ в закрытый канал для инвесторов, он бесплатный, но доступно только тем, кто инвестирует.""")
    bot.send_message(message.chat.id,'Подробнее читайте в нашей <a href="https://cryptogrammer.ru/ico">статье</a>',parse_mode="HTML")
    
@bot.message_handler(func=lambda message: message.text=="📈Торговые рекомендации")
def trade(message):
    keyboard = types.ReplyKeyboardMarkup()
    btn = types.InlineKeyboardButton(text="🤝 Присоединиться!")
    btn1= types.InlineKeyboardButton(text="🏆 Результаты сигналов")
    keyboard.row(btn,btn1)
    btn2= types.InlineKeyboardButton(text="⁉️ Вопросы и ответы")
    btn3= types.InlineKeyboardButton(text="📖 Отзывы")
    keyboard.row(btn2,btn3)
    btn4= types.InlineKeyboardButton(text="🔙 Главное меню")
    btn5= types.InlineKeyboardButton(text="🤝 Партнерская программа")
    keyboard.row(btn4,btn5)
    bot.send_message(message.chat.id, "📈Торговые рекомендации", reply_markup=keyboard)
    
@bot.message_handler(func=lambda message: message.text=="🎁Розыгрыш BTC")
def btc(message):
    bot.send_message(message.chat.id, "🎁Розыгрыш BTC")
    
@bot.message_handler(func=lambda message: message.text=="Добавить ICO")
def createico(message):
    data = db.user.find_one({"id":int(message.from_user.id)})
    if data['permissions']['is_admin'] == "true":
        bot.send_message(message.chat.id, "Введите имя ICO и описание в формате: ИМЯ ICO : ОПИСАНИЕ")
        bot.register_next_step_handler(message,ico_name)
        
def ico_name(message):
    data = db.user.find_one({"id":int(message.from_user.id)})
    if data['permissions']['is_admin'] == "true":
        s = message.text.split(':')
        create_ico(s[0],s[1])
    
@bot.message_handler(func=lambda message: message.text=="📖База знаний")
def DB(message):
    bot.send_message(message.chat.id, "📖База знаний")
    
@bot.message_handler(func=lambda message: message.text=="💵Покупка BTC")
def trade_btc(message):
    bot.send_message(message.chat.id, "Описание: объемы от 1 BTC до 1000 BTC при личной встрече за наличный расчет\nДо 1 BTC можете купить в боте: ссылка с рефкой")
    
@bot.message_handler(commands=['change'])
def change(message):
    keyboard = types.ReplyKeyboardMarkup()
    btn = types.InlineKeyboardButton(text="📱 Изменить номер телефона")
    btn1= types.InlineKeyboardButton(text="📨 Изменить Email")
    btn2= types.InlineKeyboardButton(text="💳 Изменить ETH кошелек")
    btn3= types.InlineKeyboardButton(text="🔙 Главное меню")
    keyboard.row(btn,btn1)
    keyboard.row(btn2,btn3)
    bot.send_message(message.chat.id, "Хочешь изменить данные? Выбирай, что именно:",reply_markup=keyboard)
    
@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    keyboard = types.InlineKeyboardMarkup()
    data = db.user.find_one({"id":int(call.from_user.id)})
    s = call.data.split("_")
    if s[1] == "eth":
        if data['eth_addr'] == None:
            bot.send_message(s[0], "💳 У Вас не задан ETH адрес:")
        else:
            bot.send_message(s[0], "💳 Ваш текущий адрес: %s" % data['eth_addr'])
        bot.send_message(s[0], "💵 Баланс кошелька, привязанного в кабинете: %s Eth" % get_balance(call.from_user.id))
        bot.send_message(s[0], "️❕ Вы всегда можете задать новый адрес командой: /change")
        bot.send_message(s[0], "⚠️ Пожалуйста, НЕ вводите адрес биржевого ETH кошелька")
    elif s[1] == "admin":
        bot.send_message(s[0], "че пацан админ??",reply_markup=admin(call.from_user.id))
    elif s[1] == "modelA":
        cnt = 0
        ico = db.ico.find()
        for i in ico:
            keyboard.add(types.InlineKeyboardButton(text="✅ "+i['ico'],callback_data="1"))
        bot.send_message(s[0], "Просмотр пректов",reply_markup=keyboard)
    elif s[1] == "modelB":
        btn = types.InlineKeyboardButton(text="✅ Я оплатил", callback_data=s[0]+ "_paid")
        keyboard.add(btn)
        bot.send_message(s[0], '💳 Для участия пришлите ETH на этот кошелек, дождитесь статуса ✅ Success и нажмите "Я оплатил" 👇\nЕсли транзакция не будет подтверждена с первого раза, пожалуйста, попробуйте еще раз через 10 минут.',reply_markup=keyboard)
        
    elif s[1] == "deposit":
        bot.send_message(s[0], "Здесь Вы можете пополнить баланс Вашего кошелька")
        bot.send_message(s[0], "Для этого перешлите ETH на Ваш личный кошелек: %s" % get_deposit_addr(call.from_user.id))
    elif s[1] == "history":
        bot.send_message(s[0], "️📗 Список ваших последних транзакций:")
        bot.send_message(s[0], "❕ У вас еще нет транзакций.")
    elif s[1] == "phone":
        if data['phone'] == None:
            bot.send_message(s[0], "📱 У Вас не задан номер")
        else:
            bot.send_message(s[0], "📱 Ваш текущий номер: %s" % data['phone'])
        bot.send_message(s[0], "️❕ Вы всегда можете задать новый номер командой: /change")
    elif s[1] == "email":
        if data['email'] == None:
            bot.send_message(s[0], "📨 У Вас не задан Email")
        else:
            bot.send_message(s[0], "📨 Ваш текущий Email: %s" % data['email'])
        bot.send_message(s[0], "️❕ Вы всегда можете задать новый Email командой: /change")
    elif s[1] == "access":
        btn = types.InlineKeyboardButton(text="✅ Я оплатил", callback_data=s[0]+ "_paid")
        btn1 = types.InlineKeyboardButton(text="(если True)✅ Присоединиться", callback_data=s[0] + "_p")
        keyboard.add(btn)
        bot.send_message(s[0], '''💳 Для доступа в чат пришлите сумму ETH, соответствующую выбранному сроку, на этот кошелек, дождитесь статуса ✅ Success и нажмите "Я оплатил" 👇\nЕсли транзакция не будет подтверждена с первого раза, пожалуйста, попробуйте еще раз через 10 минут.''')
        bot.send_message(s[0], '''⚠️ Сумма должна быть точно равной указанным!\nИначе доступ не откроется в автоматическом режиме.''',reply_markup=keyboard)


# In[4]:


def main():
    signal.signal(signal.SIGINT, signal_handler)
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as err:
            time.sleep(30)

def signal_handler(signal_number, frame):
    print('Received signal ' + str(signal_number)
          + '. Trying to end tasks and exit...')
    bot.stop_polling()
    sys.exit(0)

if __name__ == "__main__":
    main()

