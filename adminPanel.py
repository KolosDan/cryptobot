
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


# In[8]:
  
def admin(_id):
    keys = types.ReplyKeyboardMarkup()
    btn = types.InlineKeyboardButton(text="Добавить ICO")
    btn1= types.InlineKeyboardButton(text="Закрыть ICO")
    keys.row(btn,btn1)
    btn2= types.InlineKeyboardButton(text="Задать эксперт-кошелек")
    btn3= types.InlineKeyboardButton(text="Изменить эксперт-кошелек")
    keys.row(btn2,btn3)
    btn4= types.InlineKeyboardButton(text="🔙 Главное меню")
    keys.row(btn4)
    return keys

