
# coding: utf-8
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
import cherrypy

token = ""
bot = telebot.TeleBot(token)
db = MongoClient('', username = '', password='',authSource='').
ico = ICO()
user_dict = {}
tr_dict = {}

WEBHOOK_HOST = ''
WEBHOOK_PORT = 443  
WEBHOOK_LISTEN = '0.0.0.0'

WEBHOOK_SSL_CERT = '/root/webbot/webhook_cert.pem'  
WEBHOOK_SSL_PRIV = '/root/webbot/webhook_pkey.pem' 

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (token)


class WebhookServer(object):
    @cherrypy.expose
    def index(self):
        if 'content-length' in cherrypy.request.headers and                         'content-type' in cherrypy.request.headers and                         cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return ''
        else:
            raise cherrypy.HTTPError(403)

@bot.message_handler(commands=['start'])
def start(message):
    if create_user(message.from_user.id,message.from_user.username) == False:
        bot.send_message(message.chat.id, "Ой-ой, не удалось записать вас в базу.\nПопробуйте удалить диалог и зайти снова\nПростите за неудобства:(")
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

@bot.message_handler(func=lambda message: message.text=="Далее ⏩")
def forward(message):  
    data = db.user.find_one({"id":int(message.from_user.id)})
    if data['is_admin'] == True:
        bot.send_message(message.chat.id, "Меню 2",reply_markup=admin2(message.from_user.id))
@bot.message_handler(func=lambda message: message.text=="◀️Назад")
def back(message):
    data = db.user.find_one({"id":int(message.from_user.id)})
    if data['is_admin'] == True:
        bot.send_message(message.chat.id, "Меню",reply_markup=admin(message.from_user.id))
@bot.message_handler(func=lambda message: message.text=="Далее▶️")
def forward2(message):
    data = db.user.find_one({"id":int(message.from_user.id)})
    if data['is_admin'] == True:
        bot.send_message(message.chat.id, "Меню 3",reply_markup=admin3(message.from_user.id))
@bot.message_handler(func=lambda message: message.text=="⏪Назад")
def back2(message):  
    data = db.user.find_one({"id":int(message.from_user.id)})
    if data['is_admin'] == True:
        bot.send_message(message.chat.id, "Меню 2",reply_markup=admin2(message.from_user.id))
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
    bot.send_message(message.chat.id, "Теперь вы НЕ сможете вывести деньги через админ-панель с этого кошелька")


@bot.message_handler(func=lambda message: message.text=="⁉️ Вопросы и ответы")
def answers(message):
    keyboard = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(text="1.Почему подписка на торговые рекомендации столько стоит?", callback_data=str(message.chat.id)+"_q_1")
    btn1= types.InlineKeyboardButton(text="2.Как я могу быть уверен что вы не мошенники?", callback_data=str(message.chat.id)+"_q_2")
    btn2= types.InlineKeyboardButton(text="3.Сколько сигналов вы предоставляете?", callback_data=str(message.chat.id)+"_q_3")
    btn3= types.InlineKeyboardButton(text="4.Что если я не могу себе позволить подписку?",callback_data=str(message.chat.id)+"_q_4")
    btn4= types.InlineKeyboardButton(text="5.На какой бирже я должен торговать? ",callback_data=str(message.chat.id)+"_q_5")
    btn5= types.InlineKeyboardButton(text="6.На чем вы основываете свои сигналы?",callback_data=str(message.chat.id)+"_q_6")
    btn6= types.InlineKeyboardButton(text="7.Что если у меня остались вопросы?",callback_data=str(message.chat.id)+"_q_7")
    keyboard.row(btn)
    keyboard.row(btn1)
    keyboard.row(btn2)
    keyboard.row(btn3)
    keyboard.row(btn4)
    keyboard.row(btn5)
    keyboard.row(btn6)
    bot.send_message(message.chat.id, "Вопросы и ответы",reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text=="🤝 Присоединиться!")
def tkpart(message):
    keyboard = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(text="🥉 2х недельная подписка", callback_data=str(message.chat.id) + "_subscr_2")
    btn1= types.InlineKeyboardButton(text="🥈 Месячная подписка", callback_data=str(message.chat.id) +"_subscr_1")
    btn2= types.InlineKeyboardButton(text="🥇 Подписка на 6м", callback_data=str(message.chat.id) +"_subscr_6")
    btn3= types.InlineKeyboardButton(text="🏆 Пожизненная подписка", callback_data=str(message.chat.id) +"_subscr_inf")
    keyboard.row(btn,btn1)
    keyboard.row(btn2,btn3)
    bot.send_message(message.chat.id, """Отлично. У нас есть различные варианты участия.

Мы предлагаем следующие пакеты:
🥉0.19 ETH - 2х недельная подписка
🥈0.3 ЕТН - месячная подписка
🥇1.8 ЕТН - подписка на 6м
🏆2.5 ЕТН - пожизненная подписка

Выбери подходящий тебе пакет и начнем.""",reply_markup=keyboard)
    

@bot.message_handler(func=lambda message: message.text=="🤝 Партнерская программа")
def referal(message):
    bot.send_message(message.chat.id, """ Вы можете стать участником нашей реферальной программы  и получить бесплатный доступ.
 Для того получения бесплатного доступа на 1 месяц вам необходимо пригласить 3х друзей, которые оплатят подписку. На получения бесплатного доступа на 3 месяца- 5 друзей. 

Что бы мы могли идентифицировать вас напишите нам c указанием приглашенных вами людей, которые оплатили подписку.  
@Uji_y @VivereEstVincere @razdva34""")

@bot.message_handler(func=lambda message: message.text=="Вопросы клиентов")
def customerQ(message):
    keybd = types.InlineKeyboardMarkup()
    for i in db.answer.find():
        b = types.InlineKeyboardButton(text="Ответить", callback_data=str(message.chat.id) + "_answer_"+str(i['username']))
        keybd.row(b)
        bot.send_message(message.chat.id,"*"+str(i["username"])+"*",parse_mode="Markdown")
        bot.send_message(message.chat.id, i["question"],reply_markup=keybd)
@bot.message_handler(func=lambda message: message.text=="👨🏻‍💻Личный кабинет")
def cabinet(message):
    keybd = types.InlineKeyboardMarkup()
    data = db.user.find_one({"id":int(message.from_user.id)})
    try:
        if data['is_admin'] == True:
            admin_button = types.InlineKeyboardButton(text="Админка", callback_data=str(message.chat.id) + "_admin")
            keybd.row(admin_button)
    except:
        bot.send_message(message.chat.id, "Похоже, что все плохо, но это не точно\nЕсли у вас серьезные проблемы с аккаунтом, то напишите @artyemk или @kolosyamba")
    b = types.InlineKeyboardButton(text="💳 ETH кошелек", callback_data=str(message.chat.id) + "_eth")
    b3= types.InlineKeyboardButton(text="🕓 История", callback_data=str(message.chat.id) +"_history")
    b4 = types.InlineKeyboardButton(text="💰 Пополнить баланс", callback_data=str(message.chat.id) + "_deposit")
    keybd.row(b,b3)
    keybd.row(b4)
    if data['is_expert'] == False:
        bot.send_message(message.chat.id, """👨🏻‍💻 Кабинет
                                            \n🔑 Вы не являетесь членом нашего закрытого сообщества Private Crypto.\nДля вас действует стандартная комиссия на ICO клуб.\nДля вас не действует скидка на оборудование для майнинга.\nДля вас не действует скидка на Приватный канал с торговыми рекомендациями.
                                            \n🆔 Ваш id клиента: %s
                                            \n💵 Баланс кошелька, привязанного в кабинете: %s Eth""" % (data["id"],get_balance(message.from_user.id)),reply_markup=keybd)
    else:
        bot.send_message(message.chat.id, """🏻‍💻 Кабинет
                                            🔑 Вы являетесь членом нашего закрытого сообщества Private Crypto.\n✅Для вас действует особая комиссия на ICO клуб.\n✅Для вас действует скидка на оборудование для майнинга.\n✅Для вас действует скидка на Приватный канал с торговыми рекомендациями.
                                            \n🆔 Ваш id клиента: %s
                                            \n💵 Баланс кошелька, привязанного в кабинете: %s Eth""" % (data["id"],get_balance(message.from_user.id)),reply_markup=keybd)

@bot.message_handler(func=lambda message: message.text=="🗣Приватный чат экспертов")
def private(message):
    bot.send_message(message.chat.id, """Здравствуйте!✌️ 

Стоимость подписки на приватный чат экспертов:
0.2 ETH / месяц
1 ETH / навсегда

В приватном канале у вас есть возможность общаться с людьми, которые давно находятся на криптовалютном рынке и имеют экспертность в таких областях как фундаментальный и технический анализ монет, успешное участие в ICO, разработка блокчейн приложений и прочее❗️ 

Польза этого канала в том, что в канале создана благоприятная атмосфера, которая направлена на то, что бы каждый участник получил ответы на интересующие вопросы и помог другому. Специально для этого была сформирована такая цена, отсеивающая не заинтересованных в финансовом развитии людей. 🔥

❓В чем наши дополнительные преимущества

❗️Оформляю подписку вы получаете дополнительные скидки на наши услуги:
 - обучение. 
 - оборудование для майнинга. 
 - оборудование для хранения криптовалют. 
 - торговые рекомендации. 
 - услуги майнинг отеля. 
 - покупка и продажа криптовалюты. 

‼️ Мы оказываем поддержку нашим участникам закрытого чата экспертов. С любыми вопросами можно будет обращаться к нашим администраторам @razdva34 @VivereEstVincere @Uji_y 

✅ Процедура оплаты:
1. Перевести 0.2 ЕТН (или 1 ЕТН для бессрочной) на эфириум-кошелек 
0x264368C1D36d08715053D235426532d2177dDFd3
2. Комиссию оплачиваете вы, на наш кошелек должно попасть именно 0.2 ЕТН (или 1 ЕТН для бессрочной)
3. Обязательно внимательно перепроверьте кошелек, на который отправляете сумму.
4. Присылаете нам ID транзакции (TxID; Transaction ID; Hash)
5. Как только транзакция попадает в сеть — добавляем вас в закрытый канал. Это происходит не позднее 24 часов, обычно через 1-2 часа у вас уже есть доступ

Присоединяйтесь к нам и будем делать профит вместе ✅😎""") 
    
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
    bot.send_message(message.chat.id, """💼 ICO клуб — это быстрый и удобный инструмент для совместных инвестиций в ICO.
Мы предлагаем лучшие проекты, отобранные нашими аналитиками и участниками сообщества, и с учетом других экспертов рынка (рейтинги, лидеры мнений), на самых выгодных условиях.
\n⚠️ Перед использованием бота рекомендуем ознакомиться с инструкцией и соглашением.
\n🔑 Для доступа в приватный чат перейдите в 🗣 Приватный чат экспертов""",reply_markup=keyboard)

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
    bot.send_message(message.chat.id, "Актуальную информацию можете найти тут: https://t.me/MiningMcAfee")

@bot.message_handler(func=lambda message: message.text=="🎁Розыгрыш BTC")
def btc(message):
    bot.send_message(message.chat.id, "🎁Розыгрыш BTC")
    
def wallet_change(message):
    if _update(message.from_user.id,"eth_addr",message.text) != False:
        bot.send_message(message.chat.id, "Кошелек успешно обновлен!")
    else:
        bot.send_message(message.chat.id, "Что-то пошло не так:(\nПроверьте правильность введенных данных и нажмите на кнопку снова")
    
@bot.message_handler(func=lambda message: message.text=="🤝 Принять участие")
def takepart(message):
    keyboard = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(text="Модель 🅰️", callback_data=str(message.chat.id) + "_modelA_0")
    btn1= types.InlineKeyboardButton(text="Модель 🅱️", callback_data=str(message.chat.id) +"_modelB_")
    keyboard.row(btn,btn1)
    bot.send_message(message.chat.id, """У нас есть 2 формата участия в нашем ICO клубе:
 
Модель 🅰️ – участие в пуле на конкретно заявленное ICO.
Выбор проекта осуществляется всеми участниками из предложенных и отобранных нашей командой аналитиков.
Комиссия клуба: 5-15%

Модель 🅱️ – участие в нескольких (3-5) проектах на усмотрение клуба.
Участнику не нужно заморачиваться и тратить свое время на выбор проектов, регистрации и прочее.
Наша команда сделает это за вас. Проекты будут отобраны в течении 1-2 месяцев.
Комиссия клуба: 8%
 
Выбери свою модель участия:""",reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text=="🏆 Преимущества клуба")
def advantages(message):
    bot.send_message(message.chat.id, """⚫️ Что мы Вам предлагаем?
    Мы организовываем складчины для Pre-Sale и ICO.

    Pre-Sale – это самая ранняя стадия продажи токенов в новом проекте (проводится перед ICO по минимальной цене).

    Отличается тем, что допускаются только инвесторы с крупными депозитами (например, от 20 ETH и более), для которых заранее резервируются токены.

    Без складчины, каждому из них пришлось бы вложить довольно крупную сумму.

    Тогда как совместная покупка делает порог входа минимальным, а риски неудачи покрываются за счет крупных бонусов на Pre-Sale.

    ⚫️ Почему участвовать в складчине на Pre-Sale выгодно?

    ✔️ Бонус на токены до 70% (% бонуса зависит от проекта и количества привлеченных средств)
    ✔️ Отсутствие необходимости самостоятельной регистрации в Whitelist, KYC верификации и отслеживания времени участия.
    ✔️ Для Pre-Sale всегда резервируется крупный объём токенов.
    ✔️ Ваша покупка полностью анонимна.
    ✔️ С одной стороны вы рискуете небольшой суммой, с ней нельзя самому участвовать в Pre-Sale.
    ✔️ Но в то же время получаете возможность вложить большую сумму, чем дают инвесторам при публичной распродаже токенов, потому что тенденция публичных распродаж – уменьшать индивидуальную капитализацию.

    На стадии ICO их вам может не хватить или не успеете купить из-за небольшого Hard Cap и высокого хайпа.

    Также Вы получите доступ в закрытый канал для инвесторов, он бесплатный, но доступно только тем, кто инвестирует.
    Ознакомиться с тем, как работает складчина, Вы так же можете из <a href="http://telegra.ph/Kak-kupit-tokeny-po-samoj-nizkoj-cene-na-stadii-Pre-Sale-i-poluchit-samye-bolshie-bonusy-03-06-2">статьи</a>""",parse_mode="HTML")
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
    bot.send_message(message.chat.id, """📚 Про криптовалюты во всех их проявлениях нашей командой написано уже очень много материала. Поэтому для вашего удобства я объединил его весь во всеобъемлющую Базу Знаний. 

http://telegra.ph/Biblioteka-znanij-ot-Dzhona-Makafi-04-04-2

🔝 В ней собраны все-все статьи по самым разным направлениям - трейдинг, ICO, анализ, технические тонкости и т.д.. Эта База уникальна так как в ней максимальная концентрация контента.

Читайте, прокачивайте свои знания и делайте иксы!""")
    
@bot.message_handler(func=lambda message: message.text=="💵Покупка BTC")
def trade_btc(message):
    keyboard = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(text="Оставить заявку!",callback_data=str(message.chat.id)+"_trade_"+str(message.from_user.username))
    keyboard.row(btn)
    bot.send_message(message.chat.id, """Предоставляем услуги в Москве по:

#ОБМЕН любые объемы (от 1 до 1000 BTC).
💵👉🏼🌕USD/BTC | RUB/BTC
🌕👉🏼💵BTC/USD | BTC/RUB

💹 Bitstamp/Bitfinex
🏦 Сделки в офисе/банке
🔥 Работаем с безналом 

💰 Оставьте вашу заявку:""",reply_markup=keyboard)
    
@bot.message_handler(commands=['change'])
def change(message):
    bot.send_message(message.chat.id, "Введите ETH кошелек")
    bot.register_next_step_handler(message,wallet_change)

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
    db.answer.insert_one({"username":message.from_user.username,"question":message.text})
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
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, "️Ошибка, проверьте правильность данных")
    
@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    keyboard = types.InlineKeyboardMarkup()
    data = db.user.find_one({"id":int(call.from_user.id)})
    s = call.data.split("_")
    if s[1] == "eth":
        if data['eth_addr'] == None:
            bot.send_message(s[0], "💳 У Вас не задан ETH адрес")
        else:
            bot.send_message(s[0], "💳 Ваш текущий адрес: %s" % data['eth_addr'])
        bot.send_message(s[0], "️❕ Вы всегда можете задать новый адрес командой: /change")
        bot.send_message(s[0], "⚠️ Пожалуйста, НЕ вводите адрес биржевого ETH кошелька")
    elif s[1] == "admin":
        bot.send_message(s[0], "Раздел администратора",reply_markup=admin(call.from_user.id))
    elif s[1] == "modelA":
        icos = db.ico.find({'locked':True})
        print(icos.count())
        if icos.count() == 0:
            bot.send_message(s[0], "Сейчас ведется анализ и выбор проектов. Скоро в этом разделе появятся ближайшие складчины.",reply_markup=keyboard)
        else:
            for i in icos[int(s[2]):int(s[2])+5]:
                if i['ico'] != "modelB":
                    keyboard.add(types.InlineKeyboardButton(text="✅ "+i['ico'],callback_data=s[0]+"_"+i['ico']+"_invest"))
            keyboard.add(types.InlineKeyboardButton(text="Дальше ⏩",callback_data=s[0]+"_modelA_"+str(int(s[2])+5)))
            bot.send_message(s[0], "Просмотр проектов",reply_markup=keyboard)
    elif s[1] == "subscr":
        if s[2] == "2":
            bot.send_message(s[0],"""Чтобы получить 2х недельную подписку, пожалуйста пошлите 
0.19 ETH (без учета комиссий) по указанному адресу:

0x264368C1D36d08715053D235426532d2177dDFd3

✅ После подтверждения оплаты ваша подписка будет активирована и вы начнете 
получать торговые рекомендации от нашего канала.

🙏 Спасибо что выбрали нас.""")
        elif s[2] == "1":
            bot.send_message(s[0],"""Чтобы получить месячную подписку, пожалуйста пошлите 
0.3 ETH (без учета комиссий) по указанному адресу:

0x264368C1D36d08715053D235426532d2177dDFd3

✅ После подтверждения оплаты ваша подписка будет активирована и вы начнете 
получать торговые рекомендации от нашего канала.

🙏 Спасибо что выбрали нас.""")
        elif s[2] == "6":
            bot.send_message(s[0],"""Чтобы получить 6 месячную подписку, пожалуйста пошлите 
1.8 ETH (без учета комиссий) по указанному адресу:

0x264368C1D36d08715053D235426532d2177dDFd3

✅ После подтверждения оплаты ваша подписка будет активирована и вы начнете 
получать торговые рекомендации от нашего канала.

🙏 Спасибо что выбрали нас.""")
        elif s[2] == "inf":
            bot.send_message(s[0],"""Чтобы получить пожизненную подписку, пожалуйста пошлите 
2.5 ETH (без учета комиссий) по указанному адресу:

0x264368C1D36d08715053D235426532d2177dDFd3

✅ После подтверждения оплаты ваша подписка будет активирована и вы начнете 
получать торговые рекомендации от нашего канала.

🙏 Спасибо что выбрали нас.""")
    elif s[1] == "modelB":
        bot.send_message(s[0], '💳 Введите количество ETH, которое хотите потратить.\nНаша команда сделает самые выгодные вложения!')
        bot.register_next_step_callback(call,modelB)
    elif s[1] == "deposit":
        bot.send_message(s[0], "Здесь Вы можете пополнить баланс Вашего кошелька")
        bot.send_message(s[0], "Для этого перешлите ETH на Ваш личный кошелек:")
        bot.send_message(s[0], str(get_deposit_addr(call.from_user.id)))
    elif s[1] == "q":
        if s[2] == "1":
            bot.send_message(s[0],"""*Почему подписка на торговые рекомендации столько стоит?*
Мы стремимся формировать по настоящему ценные сигналы, устанавливая для себя и своих подписчиков приоритет не в количестве сигналов, а в их качестве

Прежде чем рекомендация попадает к вам она формируется на основании технического и фундаментального анализа, подкрепленного инсайдерской информацией

Многие каналы осуществляют перепродажу и перепост чужих рекомендаций. Отсюда формируется и цена. Воспользовавшись чужими сигналами вас просто завалят информацией без правильного риск- и манименеджмента.""",parse_mode="Markdown")
        elif s[2] == "2":
            bot.send_message(s[0],"""*Как я могу быть уверен что вы не мошенники?*
Мы осуществляем торговую деятельность уже более 1 года и за это время наши подписчики получили хороший профит. Мы также осуществляем торговлю по этим сигналам, поэтому мы не можем давать вам ложную информацию. Наша работа строиться на формировании  долгосрочных отношений с нашими партнерами. Так же можете ознакомиться с отзывами о нас.""",parse_mode="Markdown")
        elif s[2] == "3":
            bot.send_message(s[0],"""*Сколько сигналов вы предоставляете?*
В среднем у нас выходит 1-7 сигналов в день. Но бывают дни когда мы можем дать больше сигналов или вообще ни одного. Для нас главное качество
К каждому сигналу мы указываем стоп лосс, тейк профит и объем средств, которые необходимо использовать. 
Каждый сигнал в среднем приносит 5-40% прибыли.""",parse_mode="Markdown")
        elif s[2] == "4":
            bot.send_message(s[0],"""*Что если я не могу себе позволить подписку?*
Если у вас недостаточно средств для приобретения подписки, то вы можете объединиться с друзьями и организовать “складчину”. У нас нет по этому поводу ограничений, главное чтобы вы не использовали рекомендации для массовой рассылки таким образом. За это у нас бан)""",parse_mode="Markdown")
        elif s[2] == "5":
            bot.send_message(s[0],"""*На какой бирже я должен торговать? *
Необходимо иметь аккаунты на биржах Binance, Bittrex  и Poloniex. Большая часть сигналов проходит именно на Binance.""",parse_mode="Markdown")
        elif s[2] == "6":
            bot.send_message(s[0],"""*На чем вы основываете свои сигналы?*
Сигналы в большей части основаны на дорогой инсайдерской информации от наших партнеров из Кореи и США. Так же часть сигналов выходит нашим аналитическим центром""",parse_mode="Markdown")
        elif s[2] == "7":
            bot.send_message(s[0],"""Вы можете обратиться к нашим админам и задать ваш персональный вопрос.
Для нас важен каждый участник поэтому мы работаем индивидуально.
@razdva34 @Uji_y @VivereEstVincere""")
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
    elif s[1] == "access":
        btn = types.InlineKeyboardButton(text="1 месяц",callback_data=s[0]+"_chat_month")
        btn1 = types.InlineKeyboardButton(text="3 месяца",callback_data=s[0]+"_chat_3month")
        btn2 = types.InlineKeyboardButton(text="1 год",callback_data=s[0]+"_chat_year")
        btn3 = types.InlineKeyboardButton(text="Навсегда",callback_data=s[0]+"_chat_forever")
        keyboard.row(btn,btn1)
        keyboard.row(btn2,btn3)
        bot.send_message(s[0], '''Выберите свой тарифный план''',reply_markup=keyboard)
    elif s[1] == "icoinvest":
        try:
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
        except:
            bot.send_message(s[0], "Упс... ошибка на сервере. Попробуйте провести операцию заново с самого начала\nПростите за неудобство :(")
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
    elif s[1] == "answer":
        bot.send_message(s[0],"Напишите пользователю "+"@"+ str(s[2]))
        db.answer.delete_one({'username': str(s[2])})
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
        
#---------------------------

bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                certificate=open(WEBHOOK_SSL_CERT, 'r'))

cherrypy.config.update({
    'server.socket_host': WEBHOOK_LISTEN,
    'server.socket_port': WEBHOOK_PORT,
    'server.ssl_module': 'builtin',
    'server.ssl_certificate': WEBHOOK_SSL_CERT,
    'server.ssl_private_key': WEBHOOK_SSL_PRIV
})
cherrypy.quickstart(WebhookServer(), WEBHOOK_URL_PATH, {'/': {}})
