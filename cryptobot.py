
# coding: utf-8

# In[1]:


import telebot
import signal
from backend import *
from backend import _update
from pymongo import MongoClient
import sys
import time
from adminPanel import *
import time
from telebot import types


# In[2]:


token = "564747088:AAEAP-YnUgtqDfo--lGZNi89VOGR_cWfyYE"
bot = telebot.TeleBot(token)
db = MongoClient('213.183.48.143').cryptobot
ico = ICO()
user_dict = {}
tr_dict = {}


# In[3]:


@bot.message_handler(commands=['start'])
def start(message):
    create_user(message.from_user.id,message.from_user.username)
    keyboard = types.ReplyKeyboardMarkup()
    btn= types.InlineKeyboardButton(text="👨🏻‍💻Личный кабинет")
    btn1 = types.InlineKeyboardButton(text="💼ICO клуб")
    keyboard.row(btn,btn1)
    btn2= types.InlineKeyboardButton(text="📈Торговые рекомендации")
    btn3= types.InlineKeyboardButton(text="🗣Приватный чат экспертов")
    keyboard.row(btn2,btn3)
    btn4= types.InlineKeyboardButton(text="🎁Розыгрыш BTC")
    btn5= types.InlineKeyboardButton(text="📖База знаний")
    keyboard.row(btn4,btn5)
    btn6= types.InlineKeyboardButton(text="💵Покупка BTC")
    btn7= types.InlineKeyboardButton(text="🔌Майнинг, оборудование")
    keyboard.row(btn6,btn7)
    bot.send_message(message.chat.id, "👋 Приветствуем, %s! В главном меню Вы можете выбрать то, что Вас интересует:" % message.from_user.first_name,reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text=="Посмотреть вложения в ICO")
def createico(message):
    data = db.user.find_one({"id":int(message.from_user.id)})
    if data['is_admin'] == True:
        icos = db.ico.find()
        keyboard = types.InlineKeyboardMarkup()
        for i in icos:
            keyboard.add(types.InlineKeyboardButton(text=i['ico'],callback_data=str(message.chat.id)+'_getcontr_'+i['ico']))
        bot.send_message(message.chat.id, "Выберите ICO:",reply_markup=keyboard)
@bot.message_handler(func=lambda message: message.text=="Добавить ICO")
def createico(message):
    data = db.user.find_one({"id":int(message.from_user.id)})
    if data['is_admin'] == True:
        bot.send_message(message.chat.id, "Введите имя ICO")
        bot.register_next_step_handler(message,ico_name)
        
def ico_name(message):
    ico.name = message.text
    bot.send_message(message.chat.id, "Введите краткое описание ICO")
    bot.register_next_step_handler(message,ico_description)
    
def ico_description(message):
    ico.description = message.text
    if create_ico(ico.name,ico.description) != False:
        bot.send_message(message.chat.id, "ICO Добавлено!") 
    else:
        bot.send_message(message.chat.id, "Что-то пошло не так, возможно такой проект уже есть") 
        
@bot.message_handler(func=lambda message: message.text=="Открыть/закрыть ICO")
def lockico(message):
    data = db.user.find_one({"id":int(message.from_user.id)})
    if data['is_admin'] == True:
        icos = db.ico.find()
        keyboard = types.InlineKeyboardMarkup()
        for i in icos:
            if i['locked'] == True:         
                keyboard.add(types.InlineKeyboardButton(text=i['ico']+'(Открыто)',callback_data=str(message.chat.id)+'_lockico_'+i['ico']))
            else:
                keyboard.add(types.InlineKeyboardButton(text=i['ico']+'(Закрыто)',callback_data=str(message.chat.id)+'_lockico_'+i['ico']))
        bot.send_message(message.chat.id, "Выберите ICO:",reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text=="Далее ▶️")
def forward(message):  
    data = db.user.find_one({"id":int(message.from_user.id)})
    if data['is_admin'] == True:
        bot.send_message(message.chat.id, "Меню 2",reply_markup=admin2(message.from_user.id))
@bot.message_handler(func=lambda message: message.text=="◀️  Назад")
def back(message):
    data = db.user.find_one({"id":int(message.from_user.id)})
    if data['is_admin'] == True:
        bot.send_message(message.chat.id, "Меню",reply_markup=admin(message.from_user.id))
@bot.message_handler(func=lambda message: message.text=="Посмотреть баланс ICO")
def icobalance(message):
    icos = db.ico.find()
    keyboard = types.InlineKeyboardMarkup()
    for i in icos:
        keyboard.add(types.InlineKeyboardButton(text=i['ico'],callback_data=str(message.chat.id)+'_icobalance_'+i['ico']))
    bot.send_message(message.chat.id, "Выберите ICO:",reply_markup=keyboard)
@bot.message_handler(func=lambda message: message.text=="Вывести деньги с ICO")
def transferFromIco(message):
    data = db.user.find_one({"id":int(message.from_user.id)})
    if data['is_admin'] == True:
        icos = db.ico.find()
        keyboard = types.InlineKeyboardMarkup()
        for i in icos:
            keyboard.add(types.InlineKeyboardButton(text=i['ico'],callback_data=str(message.chat.id)+'_transferfrom_'+i['ico']))
        bot.send_message(message.chat.id, "Выберите ICO:",reply_markup=keyboard)
    
@bot.message_handler(func=lambda message: message.text=="Изменить эксперт-кошелек")
def updatexpert(message):
    data = db.user.find_one({"id":int(message.from_user.id)})
    if data['is_admin'] == True:
        bot.send_message(message.chat.id, "Впишите новый адрес")
        bot.register_next_step_handler(message,updatexpert_2)
    
def updatexpert_2(message):
    if update_expert(message.text) != False:
        bot.send_message(message.chat.id, "Обновлено успешно")
    else:
        bot.send_message(message.chat.id, "Ошибка, проверьте правильность введенных данных")
    
@bot.message_handler(func=lambda message: message.text=="Задать эксперт-кошелек")
def addexpert(message):
    bot.send_message(message.chat.id, "Впишите адрес")
    bot.register_next_step_handler(message,addexpert_2)
    
def addexpert_2(message):
    if add_expert(message.text) != False:
        bot.send_message(message.chat.id, "Адрес изменен")
    else:
        bot.send_message(message.chat.id, "Кошелек уже создан")
    
@bot.message_handler(func=lambda message: message.text=="Изменить кошелек модели B")
def changeModelB(message):
    data = db.user.find_one({"id":int(message.from_user.id)})
    if data['is_admin'] == True:
        bot.send_message(message.chat.id, "Введите новый кошелек")
        bot.register_next_step_handler(message,changeModelB_step2)
def changeModelB_step2(message):
    update_modelb(message.text)
    bot.send_message(message.chat.id, "Кошелек изменен")
        
@bot.message_handler(func=lambda message: message.text=="👨🏻‍💻Личный кабинет")
def cabinet(message):
    keybd = types.InlineKeyboardMarkup()
    data = db.user.find_one({"id":int(message.from_user.id)})
    if data['is_admin'] == True:
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
    bot.send_message(message.chat.id, "💵 Баланс кошелька, привязанного в кабинете: %s Eth" % get_balance(message.from_user.id))
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
    btn= types.InlineKeyboardButton(text="👨🏻‍💻Личный кабинет")
    btn1 = types.InlineKeyboardButton(text="💼ICO клуб")
    keyboard.row(btn,btn1)
    btn2= types.InlineKeyboardButton(text="📈Торговые рекомендации")
    btn3= types.InlineKeyboardButton(text="🗣Приватный чат экспертов")
    keyboard.row(btn2,btn3)
    btn4= types.InlineKeyboardButton(text="🎁Розыгрыш BTC")
    btn5= types.InlineKeyboardButton(text="📖База знаний")
    keyboard.row(btn4,btn5)
    btn6= types.InlineKeyboardButton(text="💵Покупка BTC")
    btn7= types.InlineKeyboardButton(text="🔌Майнинг, оборудование")
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
        bot.send_message(message.chat.id, "Что-то пошло не так:(\nПроверьте правильность введенных данных и нажмите на кнопку снова")
        
@bot.message_handler(func=lambda message: message.text=="📨 Изменить Email")
def email(message):
    bot.send_message(message.chat.id, "Введите Email")
    bot.register_next_step_handler(message,email_change)

def email_change(message):
    if _update(message.from_user.id,"email",message.text) != False:
        bot.send_message(message.chat.id, "Email успешно обновлен!")
    else:
        bot.send_message(message.chat.id, "Что-то пошло не так:(\nПроверьте правильность введенных данных и нажмите на кнопку снова")
    
@bot.message_handler(func=lambda message: message.text=="💳 Изменить ETH кошелек")
def eth(message):
    bot.send_message(message.chat.id, "Введите ETH кошелек")
    bot.register_next_step_handler(message,wallet_change)
    
def wallet_change(message):
    if _update(message.from_user.id,"eth_addr",message.text) != False:
        bot.send_message(message.chat.id, "Кошелек успешно обновлен!")
    else:
        bot.send_message(message.chat.id, "Что-то пошло не так:(\nПроверьте правильность введенных данных и нажмите на кнопку снова")
    
@bot.message_handler(func=lambda message: message.text=="🤝 Принять участие")
def takepart(message):
    keyboard = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(text="Модель 🅰️", callback_data=str(message.chat.id) + "_modelA")
    btn1= types.InlineKeyboardButton(text="Модель 🅱️", callback_data=str(message.chat.id) +"_modelB")
    keyboard.row(btn,btn1)
    bot.send_message(message.chat.id, "У нас есть 2 формата участия в нашем ICO клубе:")
    bot.send_message(message.chat.id, "Модель 🅰️ – участие в пуле на конкретное заявленное ICO.\nВыбор проекта осуществляется всеми участниками из предложенных и отобранных нашей командой аналитиков.\nКомиссия клуба: 5-15%")
    bot.send_message(message.chat.id, "Модель 🅱️ – участие в 5 проектах на усмотрение клуба.\nУчастника не нужно заморачиваться и тратить свое время на выбор проектов, регистрации и прочее.\nНаша команда сделает это за вас. Проекты будут отобраны в течении 1-2 месяцев.\nКомиссия клуба: 12%")
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
    bot.send_message(message.chat.id, "Хотите изменить данные? Выбирайте, что именно:",reply_markup=keyboard)

def syka(call,_id,name):
    user = Payment()
    user_dict[_id] = user
    user_dict[_id]._id = _id
    user_dict[_id].name = name
    bot.send_message(_id,'Отличный выбор!')
    bot.send_message(_id,'Введите количество ETH, которое хотите вложить:')
    bot.register_next_step_callback(call,pizdec)
    
def pizdec(message):
    try:
        var = float(message.text)
        user_dict[str(message.chat.id)].value = var
        keyboard = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton(text="✅ Подтвердить", callback_data=str(message.chat.id)+ "_icoinvest_")
        keyboard.row(btn)
        bot.send_message(message.chat.id,'Вы хотите перевести ' + str(user_dict[str(message.chat.id)].value) + ' ETH на счет ' + str(user_dict[str(message.chat.id)].name),reply_markup=keyboard) 
    except ValueError:
        bot.send_message(message.chat.id,'Похоже, что Вы ввели что-то неправильно\nНажмите на кнопу снова')
        
def modelB(message):
    try:
        var = float(message.text)
        keyboard = types.InlineKeyboardMarkup()
        user = Payment()
        user_dict[str(message.from_user.id)] = user
        user_dict[str(message.from_user.id)]._id = message.chat.id
        user_dict[str(message.chat.id)].value = var
        btn = types.InlineKeyboardButton(text="✅ Подтвердить", callback_data=str(message.chat.id)+ "_icoinvest_modelB")
        keyboard.row(btn)
        bot.send_message(message.chat.id,'Вы хотите перевести ' + str(user_dict[str(message.chat.id)].value)+' ETH',reply_markup=keyboard)
    except ValueError:
        bot.send_message(message.chat.id,'Похоже, что Вы ввели что-то неправильно\nНажмите на кнопу снова')
        
def question(message):
    print(message.text)
    bot.send_message(message.chat.id, "️Ваш вопрос напрален администратору\nС вами свяжутся в ближайшее время")
    
def transferFrom_step3(call,name):
    transfer = transferFrom()
    tr_dict[call.from_user.id] = transfer
    tr_dict[call.from_user.id].name = name
    bot.send_message(call.from_user.id, "️Введите адрес, на который будут переведены деньги (ВНИМАТЕЛЬНО проверьте корректность данных)")
    bot.register_next_step_callback(call,transferFrom_step4)
def transferFrom_step4(message):
    tr_dict[message.from_user.id].addr = message.text
    bot.send_message(message.chat.id, "️Введите сумму для перевода (%s доступно)" % get_ico_money(tr_dict[message.from_user.id].name))
    bot.register_next_step_handler(message,transferFrom_step5)
def transferFrom_step5(message):
    try:
        tr_dict[message.from_user.id].value = float(message.text)
        if transfer_from_ico(tr_dict[message.from_user.id].name,tr_dict[message.from_user.id].addr,tr_dict[message.from_user.id].value) != False:
            bot.send_message(message.chat.id, "️Транзакция успешно отправлена")
        else:
            bot.send_message(message.chat.id, "️Произошла ошибка")
    except:
        bot.send_message(message.chat.id, "️Ошибка, проверьте правильность данных")
    
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
        bot.send_message(s[0], "️❕ Вы всегда можете задать новый адрес командой: /change")
        bot.send_message(s[0], "⚠️ Пожалуйста, НЕ вводите адрес биржевого ETH кошелька")
    elif s[1] == "admin":
        bot.send_message(s[0], "че пацан админ??",reply_markup=admin(call.from_user.id))
    elif s[1] == "modelA":
        cnt = 0
        icos = db.ico.find({'locked':True})
        for i in icos:
            if i['ico'] != "modelB":
                keyboard.add(types.InlineKeyboardButton(text="✅ "+i['ico'],callback_data=s[0]+"_"+i['ico']+"_invest"))
        bot.send_message(s[0], "Просмотр проектов",reply_markup=keyboard)
    elif s[1] == "modelB":
        bot.send_message(s[0], '💳 Введите количество ETH, которое хотите потратить.\nНаша команда сделает самые выгодные вложения!')
        bot.register_next_step_callback(call,modelB)
    elif s[1] == "deposit":
        bot.send_message(s[0], "Здесь Вы можете пополнить баланс Вашего кошелька")
        bot.send_message(s[0], "Для этого перешлите ETH на Ваш личный кошелек:")
        bot.send_message(s[0], str(get_deposit_addr(call.from_user.id)))
    elif s[1] == "history":
        bot.send_message(s[0], "️📗 Список ваших последних операций:")
        for i in data['operations'][-5:]:
            if i['op'] == 'contribute':
                bot.send_message(s[0],"*" + str(i['timestamp']).split('.')[0]+"*",parse_mode="Markdown")
                bot.send_message(s[0],"Вы инвестировали "+str(i['eth'])+" ETH в "+i['ico'])
            elif i['op'] == 'create_user':
                bot.send_message(s[0],"*"+str(i['timestamp'].split('.')[0])+"*",parse_mode="Markdown")
                bot.send_message(s[0], "Создан пользователь")
            elif i['op'] == "expert":
                bot.send_message(s[0],"*"+str(i['timestamp'].split('.')[0])+"*",parse_mode="Markdown")
                bot.send_message(s[0], "Получен доступ к чату экспертов")
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
        btn = types.InlineKeyboardButton(text="1 месяц",callback_data=s[0]+"_chat_month")
        btn1 = types.InlineKeyboardButton(text="3 месяца",callback_data=s[0]+"_chat_3month")
        btn2 = types.InlineKeyboardButton(text="1 год",callback_data=s[0]+"_chat_year")
        btn3 = types.InlineKeyboardButton(text="Навсегда",callback_data=s[0]+"_chat_forever")
        keyboard.row(btn,btn1)
        keyboard.row(btn2,btn3)
        bot.send_message(s[0], '''Выберите свой тарифный план''',reply_markup=keyboard)
    elif s[1] == "icoinvest":
        if s[2] == "modelB":
            if contribute(int(user_dict[str(call.from_user.id)]._id),"modelB",user_dict[str(call.from_user.id)].value) != False:
                bot.send_message(s[0], "Транзакция успешно отправлена")
                if data['is_expert'] == False:
                    time = str(datetime.date.today() + datetime.timedelta(days=31))
                    db.user.update_one({'id':call.from_user.id}, {'$set':{'is_expert': time}})
                    btn = types.InlineKeyboardButton(text="Чат",url='https://habrahabr.ru')
                    keyboard.row(btn)
                    bot.send_message(s[0], "🎁 В подарок вам дается доступ на 1 месяц к Приватному чату экспертов Private Crypto.",reply_markup=keyboard)
            else:
                bot.send_message(s[0], "У вас недостаточно средств для данной операции или сумма транзакции слишком мала:(")
        else:
            if contribute(int(user_dict[str(call.from_user.id)]._id),user_dict[str(call.from_user.id)].name,user_dict[str(call.from_user.id)].value) != False:
                bot.send_message(s[0], "Транзакция успешно отправлена")
            else:
                bot.send_message(s[0], "У вас недостаточно средств для данной операции или сумма транзакции слишком мала:(")
    elif s[1] == "getcontr":
        if get_contributors(s[2]) ==[]:
            bot.send_message(s[0], 'Еще нет вложений')
        for i in get_contributors(s[2]):
            try:
                bot.send_message(s[0], 'Пользователь ' + i[0] + ' инвестировал в ' + i[2]['ico'] + ' ' + str(i[2]['eth']) + ' ETH')
                bot.send_message(s[0], 'Его личный ETH_address: ' + str(i[1]))
                bot.send_message(s[0], 'TX HASH: ' + i[2]['tx_hash'])
            except:
                pass
    elif s[1] == "transferfrom":
        transferFrom_step3(call,s[2])
    elif s[1] == "icobalance":
        bot.send_message(s[0],"Баланс "+str(get_ico_money(s[2]))+" ETH")
    elif s[1] == "lockico":
        change_lock(s[2])
        bot.send_message(s[0], "Успешно")
    elif s[1] == "chat":
        if get_expert(call.from_user.id,s[2]) != False:
            btn = types.InlineKeyboardButton(text="Чат",url='https://habrahabr.ru')
            keyboard.row(btn)
            bot.send_message(s[0], "Транзакция успешно отправлена",reply_markup=keyboard)
        else:
            bot.send_message(s[0], "Похоже, что у вас не хватает денег на счету:(\nКошелек можно пополнить в личном кабинете")
    elif s[1] == "question":
        bot.send_message(s[0], "Задайте свой вопрос")
        bot.register_next_step_callback(call,question)
    elif s[2] == "invest":
        key = types.InlineKeyboardMarkup()
        i = db.ico.find_one({"ico":s[1]})
        key.add(types.InlineKeyboardButton(text="💵 Инвестировать",callback_data=s[0]+"_"+i['ico']+"_investstep2"))
        bot.send_message(s[0],'Название ICO: '+i['ico'])
        bot.send_message(s[0],'Краткое описание: '+i['description'])
        bot.send_message(s[0],'Хотите инвестировать в данное ICO? Нажмите "инвестировать"!',reply_markup=key)
    elif s[2] == "investstep2":
        syka(call,s[0],s[1])


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


# In[6]:


get_balance('0x3d9a93c1a4be6f07939f51c44a860302086fa047')

