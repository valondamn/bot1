from cgitb import text
from email import message
import shutil
from http import client
from statistics import mean
from sys import call_tracing
from pkg_resources import require
import telebot 
from tinydb import TinyDB, Query, where
from telebot import types
import json
import os
from os import walk
import csv 
import requests

bot = telebot.TeleBot('5342565961:AAFkYRvSRt564NSt8GdczET0KIVFrXzQbBE') 

query = Query()

db = TinyDB('user.json')
TOKEN='5208293058:AAEiJnl1py8BnHlNBIAsSj3cj2jbC9WrvRU'
url = "https://api.telegram.org/bot" + TOKEN



@bot.message_handler(commands=['start'])
def button(message):
    query = Query()
    finded_users=db.search(query.id == message.from_user.id)
    
    if len(finded_users)==0:
        db.insert({'id': message.from_user.id })
    markup = types.InlineKeyboardMarkup(row_width=2)
    item = types.InlineKeyboardButton('Нужна помошь', callback_data='need')
    item2 = types.InlineKeyboardButton('Хочу помочь', callback_data='want')
    markup.add(item, item2)
    msg = bot.send_message(message.chat.id, 'Здравствуйте! Вы попали в бота министерства образования Республики Казахстан, он создан для помощи людям.\nПожалуйства выберите, что вы хотите сделать: ', reply_markup=markup)
    
@bot.message_handler(content_types="web_app_data") #получаем отправленные данные 
def answer(webAppMes):
   print(webAppMes) #вся информация о сообщении
   print(webAppMes.web_app_data.data) #конкретно то что мы передали в бота
   bot.send_message(webAppMes.chat.id,  "Спасибо за предстваленную вами информацию! С вами обязательно свяжутся для оказания помощи! ")
   webdatamessage = webAppMes.web_app_data.data
   #отправляем сообщение в ответ на отправку данных из веб-приложения 

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    query = Query()

    if call.data == "need":
        
        db.upsert({'thing': 'Нужна помощь'}, query.id == call.from_user.id)
    elif call.data == 'want':
        
        db.upsert({'thing': 'Хочу помочь'}, query.id == call.from_user.id)
    
    if call.data == "need": 
        mesg = bot.send_message(call.from_user.id,  "Введите номер телефона:")
        bot.register_next_step_handler(mesg,number)

    if call.data =="want": 
        bot.send_message(call.from_user.id, 'Пожалуйства выберите школу!', reply_markup=webAppKeyboard()) 

        
    #________________________________________________
    if call.data == "Incomplete":
        db.upsert({'status': 'Неполный'}, query.id == call.from_user.id)
        
    
    elif call.data == "Low_income":
        db.upsert({'status': 'Малообеспеченный'}, query.id == call.from_user.id)

    if call.data == "Incomplete" or call.data == "Low_income": 
        msg = bot.send_message(call.from_user.id, 'Количество детей школьного возраста:')
        bot.register_next_step_handler(msg, help1) 
    
    if  call.data == "drugoe": 
        mesg = bot.send_message(call.from_user.id,  "Введите социальный статус:")
        bot.register_next_step_handler(mesg, another)   
        

    #_________________________________________________________________________________
    print(call)
    # if not call.data:
    #     print(call)
    #     page_url = "https://vtlapp.glide.page/"
    #     requests.get(url + '/answerCallbackQuery?callback_query_id=' + call.id + '&url=' + page_url)
       
    try:
        if "men" in call.data or "wooman" in call.data: 
            finded_users=db.search(query.id == call.from_user.id)
            user=finded_users[0]
            child_num=call.data.replace('men','').replace('wooman','')
            user['childs'][f'child{child_num}']['gender']=call.data[0:-1]
            db.upsert({'childs': user['childs']}, query.id == call.from_user.id)
            mesg = bot.send_message(call.from_user.id, "Одежда(Указать: наименование, размер, рост):")
            bot.register_next_step_handler(mesg, lambda m: step2(m,child_num=child_num)) 
    except:
        pass
        
    if call.data == "add": 
        
        
        i = len(datas['_default']['1']['childs'])
        arr = datas['_default']['1']['childs']
        arr[f'child{i}'] = {}  
        
        
        
        mesg = bot.send_message(call.from_user.id, f"Ребенок {i}")
        bot.register_next_step_handler(mesg, step1) 
        
    if call.data == "off": 
        bot.send_message(call.from_user.id, "Вы закончили опрос!")
                


    
def number(message): 
    number =  message.text 
    db.upsert({'number': number}, query.id == message.from_user.id)
    mesg = bot.send_message(message.from_user.id,  "Введите ИИН:")
    bot.register_next_step_handler(mesg,status)


def status(message):
    IIN =  message.text 
    db.upsert({'IIN': IIN}, query.id == message.from_user.id)
    markup = types.InlineKeyboardMarkup(row_width=2)
    item = types.InlineKeyboardButton('Неполный', callback_data='Incomplete')
    item2 = types.InlineKeyboardButton('Малообеспеченный', callback_data='Low_income')
    item3 = types.InlineKeyboardButton('Другое...', callback_data='drugoe')
    markup.add(item, item2, item3)
    msg = bot.send_message(message.chat.id, 'Социальный статус семьи:', reply_markup=markup)
    
    

    
def another(message): 
    another  = message.text
    db.upsert({'status': another}, query.id == message.from_user.id)
    msg = bot.send_message(message.chat.id, 'Количество детей школьного возраста:')
    bot.register_next_step_handler(msg, help1)  
    


        
        


def help1(message,child_num=1):  
    sum  = message.text
    db.upsert({'Sum_children': sum}, query.id == message.from_user.id)
    child_dict={}
    for child in range(1,int(sum)+1):
        child_dict[f'child{child}']={}

    db.upsert({'childs': child_dict}, query.id == message.from_user.id)

    child_msg = str(f"Ребенок - {child_num}")
    markup = types.InlineKeyboardMarkup(row_width=2)
    item = types.InlineKeyboardButton('Мужской', callback_data=f'men{child_num}')
    item2 = types.InlineKeyboardButton('Женский', callback_data=f'wooman{child_num}')
    markup.add(item, item2 )
    msg = bot.send_message(message.chat.id, f"{child_msg}\nПол:", reply_markup=markup)
   
 
#start

def step1(message):
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    item = types.InlineKeyboardButton('Мужской', callback_data='men')
    item2 = types.InlineKeyboardButton('Женский', callback_data='wooman')
    markup.add(item, item2 )
    msg = bot.send_message(message.chat.id, "Пол:", reply_markup=markup)
   
        
def step2(message,child_num):  
    clothes  = message.text
    finded_users=db.search(query.id == message.from_user.id)
    user=finded_users[0]
    user['childs'][f'child{child_num}']['clothes']=clothes
    db.upsert({'childs': user['childs']}, query.id == message.from_user.id)
    msg = bot.send_message(message.chat.id, "Канц товары(Указать наименование):")
    bot.register_next_step_handler(msg, lambda m:step3(m,child_num))    

def step3(message,child_num):  

    Office_supplies  = message.text
    finded_users=db.search(query.id == message.from_user.id)
    user=finded_users[0]
    user['childs'][f'child{child_num}']['office_suppliers']=Office_supplies
    db.upsert({'childs': user['childs']}, query.id == message.from_user.id)
    #db.upsert({'Office_supplies': Office_supplies}, query.id == message.from_user.id)
    msg = bot.send_message(message.chat.id, "Обувь(Указать вид обуви, размер)")
    bot.register_next_step_handler(msg, lambda m:step4(m,child_num))   
    
    
# функция распределения

def step4(message,child_num): 
    shoes=message.text
    finded_users=db.search(query.id == message.from_user.id)
    user=finded_users[0]
    user['childs'][f'child{child_num}']['shoes']=shoes
    db.upsert({'childs': user['childs']}, query.id == message.from_user.id)
    markup = types.InlineKeyboardMarkup(row_width=2)
    last_child=user['Sum_children']
    if not user['childs'][f'child{last_child}']:
        msg = bot.send_message(message.chat.id,f"Данные ребенка N{child_num} заполнены")
        child_num=int(child_num)+1
        child_msg = str(f"Ребенок - {child_num}")
        markup = types.InlineKeyboardMarkup(row_width=2)
        item = types.InlineKeyboardButton('Мужской', callback_data=f'men{child_num}')
        item2 = types.InlineKeyboardButton('Женский', callback_data=f'wooman{child_num}')
        markup.add(item, item2 )
        msg = bot.send_message(message.chat.id, f"{child_msg}\nПол:", reply_markup=markup)
    else:
        bot.send_message( message.chat.id, 'Пожалуйства выберите школу!', reply_markup=webAppKeyboard()) 

def webAppKeyboard(): #создание клавиатуры с webapp кнопкой
   keyboard = types.ReplyKeyboardMarkup(row_width=1) #создаем клавиатуру
   webAppTest = types.WebAppInfo("https://trusting-difficult-collision.glitch.me/") #создаем webappinfo - формат хранения url
   one_butt = types.KeyboardButton(text="Выбрать школу...", web_app=webAppTest) #создаем кнопку типа webapp
   keyboard.add(one_butt) #добавляем кнопки в клавиатуру

   return keyboard #возвращаем клавиатуру

    


    
bot.polling(none_stop = True)