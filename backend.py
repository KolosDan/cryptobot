# coding: utf-8
from pymongo import MongoClient
import requests
import datetime
from web3.utils import validation
import re
from phonenumbers import parse, is_possible_number
from web3 import Web3, HTTPProvider




db = MongoClient('213.183.48.143').cryptobot
w3 = Web3(HTTPProvider('https://ropsten.infura.io/xSb0KCuTom59NVjS446D'))


def create_user(_id, username):
    if db.user.find_one({"id":int(_id)}) == None:
        user = {}
        user['id'] = _id
        user['username'] = username
        user['eth_addr'] = None
        user['email'] = None
        user['phone'] = None
        user['permissions'] = {'is_expert': False, 'is_admin': False}
        user['balance'] = 0.0
        user['operations'] = ['Created user ' + str(datetime.datetime.now())]
        user['deposit_addr'] = requests.post('https://api.blockcypher.com/v1/eth/main/addrs').json()
        return db.user.insert_one(user)

def update(_id,field, upd):
    if field == 'eth_addr':
        if validation.is_0x_prefixed(upd) and validation.is_address(upd) and len(upd) == 42:
            return db.user.update({'id':_id},{'$set':{'eth_addr': upd}})
    if field == 'email':
        if re.match(r"[^@]+@[^@]+\.[^@]+", upd):
            return db.user.update({'id':_id},{'$set':{'email': upd}})
    if field == 'phone':
        try:
            if is_possible_number(parse('+11235125520')):
                return db.user.update({'id':_id},{'$set':{'phone': upd}})
            else:
                return False
        except:
            return False

def create_ico(name, description):
    if name not in [item['ico'] for item in db.ico.find()]:
        return db.ico.insert_one({'ico' :name, 
                      'address' : requests.post('https://api.blockcypher.com/v1/eth/main/addrs').json(),
                      'description' : description,
                      'contributors' : [],
                             'locked':True})
    else:
        return False
    
def change_ico_lock(name):
    if db.ico.find_one({'ico': name})['locked'] == False:
        print('ICO locked')
        return db.ico.update_one({'ico': name}, {'$set':{'locked': True}})
    else:
        print('ICO unlocked')
        return db.ico.update_one({'ico': name}, {'$set':{'locked': False}})

def get_balance(_id):
    return w3.eth.getBalance('0x' + db.user.find_one({'id':_id})['deposit_addr']['address'])/1000000000000000000
