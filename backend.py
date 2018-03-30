
# coding: utf-8

# In[3]:


from pymongo import MongoClient
import requests
import datetime
from web3.utils import validation
import re
from phonenumbers import parse, is_possible_number
from web3 import Web3, HTTPProvider
import time



import rlp
from ethereum.transactions import Transaction



db = MongoClient('213.183.48.143').cryptobot
w3 = Web3(HTTPProvider('https://ropsten.infura.io/xSb0KCuTom59NVjS446D'))



def create_user(_id, username):
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
            if is_possible_number(parse(upd)):
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



def change_lock(name):
    if db.ico.find_one({'ico': name})['locked'] == False:
        print('ICO locked')
        return db.ico.update_one({'ico': name}, {'$set':{'locked': True}})
    else:
        print('ICO unlocked')
        return db.ico.update_one({'ico': name}, {'$set':{'locked': False}})




def get_balance(_id):
    balance = w3.eth.getBalance('0x' + db.user.find_one({'id':_id})['deposit_addr']['address'])/1000000000000000000
    db.user.update_one({'id':_id}, {'$set':{'balance': balance}})
    return balance



def tx(from_addr, to_addr, signature, eth_value):
   
    tx = Transaction(nonce= w3.eth.getTransactionCount(from_addr),
                        gasprice= w3.eth.gasPrice,
                        startgas= 100000,
                        to= to_addr,
                        value= int(eth_value * 1000000000000000000),
                        data = b'')
    
    tx.sign(signature)
    raw_tx = rlp.encode(tx)
    raw_tx_hex = w3.toHex(raw_tx)
    
    return w3.eth.sendRawTransaction(raw_tx_hex)



def contribute(_id, ico, eth_value):
    to_addr = '0x' + db.ico.find_one({'ico':ico})['address']['address']
    print(to_addr)
    signature = '0x' + db.user.find_one({'id':_id})['deposit_addr']['private']
    print(signature)
    from_addr = '0x' + db.user.find_one({'id':_id})['deposit_addr']['address']
    print(from_addr)
    return tx(from_addr, to_addr, signature, eth_value)



def get_deposit_addr(_id):
    return '0x' + db.user.find_one({'id':_id})['deposit_addr']['address']

