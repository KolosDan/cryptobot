
# coding: utf-8

# In[4]:


import telebot
from backend import create_ico
from telebot import types
token = "564747088:AAEAP-YnUgtqDfo--lGZNi89VOGR_cWfyYE"
bot = telebot.TeleBot(token)


# In[7]:


class Payment:
    def __init__(self):
        self._id = None
        self.name = None
        self.value = None
class ICO:
    def __init__(self):
        self.name = None
        self.description = None
        
class transferFrom:
    def __init__(self):
        self.name = None
        self.value = None
        self.addr = None

# In[8]:
  
def admin(_id):
    keys = types.ReplyKeyboardMarkup()
    btn = types.InlineKeyboardButton(text="Добавить ICO")
    btn1= types.InlineKeyboardButton(text="Открыть/закрыть ICO")
    btn2= types.InlineKeyboardButton(text="Задать эксперт-кошелек")
    btn3= types.InlineKeyboardButton(text="Изменить эксперт-кошелек")
    btn4= types.InlineKeyboardButton(text="Далее ▶️")
    btn5= types.InlineKeyboardButton(text="🔙 Главное меню")
    keys.row(btn,btn1)
    keys.row(btn2,btn3)
    keys.row(btn4,btn5)
    return keys

def admin2(_id):
    keys = types.ReplyKeyboardMarkup()
    btn= types.InlineKeyboardButton(text="Посмотреть баланс ICO")
    btn1= types.InlineKeyboardButton(text="Вывести деньги с ICO")
    btn2 =types.InlineKeyboardButton(text="Изменить кошелек модели B")
    btn3 =types.InlineKeyboardButton(text="Посмотреть вложения в ICO")
    btn4 =types.InlineKeyboardButton(text="◀️  Назад")
    btn5 =types.InlineKeyboardButton(text="🔙 Главное меню")
    keys.row(btn,btn1)
    keys.row(btn2,btn3)
    keys.row(btn4,btn5)
    return keys

