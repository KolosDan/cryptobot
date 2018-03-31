
# coding: utf-8

# In[1]:


from pymongo import MongoClient
import requests
import datetime
from web3.utils import validation
import re
from phonenumbers import parse, is_valid_number
from web3 import Web3, HTTPProvider
import time

# In[2]:


import rlp
from ethereum.transactions import Transaction


# In[130]:


db = MongoClient('213.183.48.143').cryptobot
w3 = Web3(HTTPProvider('https://ropsten.infura.io/xSb0KCuTom59NVjS446D'))


# In[4]:

def create_user(_id, username):
    if db.user.find_one({"username":username}) == None:
        user = {}
        user['id'] = _id
        user['username'] = username
        user['eth_addr'] = None
        user['email'] = None
        user['phone'] = None
        user['is_expert'] = False
        user['is_admin'] = False
        user['balance'] = 0.0
        user['operations'] = ['Created user ' + str(datetime.datetime.now())]
        user['deposit_addr'] = requests.post('https://api.blockcypher.com/v1/eth/main/addrs').json()

        return db.user.insert_one(user)

# In[5]:


def _update(_id,field, upd):
    if field == 'eth_addr':
        if validation.is_0x_prefixed(upd) and validation.is_address(upd) and len(upd) == 42:
            return db.user.update({'id':_id},{'$set':{'eth_addr': upd}})
        else:
            return False
    elif field == 'email':
        if re.match(r"[^@]+@[^@]+\.[^@]+", upd):
            return db.user.update({'id':_id},{'$set':{'email': upd}})
        else:
            return False
    elif field == 'phone':
        try:
            if is_valid_number(parse(upd)):
                return db.user.update({'id':_id},{'$set':{'phone': upd}})
            else:
                return False
        except:
            return False


# In[6]:


def create_ico(name, description):
    if name not in [item['ico'] for item in db.ico.find()]:
        return db.ico.insert_one({'ico' :name, 
                      'address' : requests.post('https://api.blockcypher.com/v1/eth/main/addrs').json(),
                      'description' : description,
                      'contributors' : [],
                             'locked':True})
    else:
        return False


# In[7]:


def change_lock(name):
    if db.ico.find_one({'ico': name})['locked'] == False:
        print('ICO locked')
        return db.ico.update_one({'ico': name}, {'$set':{'locked': True}})
    else:
        return db.ico.update_one({'ico': name}, {'$set':{'locked': False}})


# In[8]:


def get_balance(_id):
    balance = w3.eth.getBalance('0x' + db.user.find_one({'id':_id})['deposit_addr']['address'])/1000000000000000000
    db.user.update_one({'id':_id}, {'$set':{'balance': balance}})
    return balance


# In[118]:


def tx(from_addr, to_addr, signature, eth_value):
    est_fee = w3.eth.estimateGas({'to':to_addr, 'from': from_addr, 'value': int(eth_value*1000000000000000000)}) * w3.eth.gasPrice
    tx = Transaction(nonce= w3.eth.getTransactionCount(from_addr),
                        gasprice= w3.eth.gasPrice,
                        startgas= 21000,
                        to= to_addr,
                        value= int((eth_value * 1000000000000000000) - est_fee),
                        data = b'')
    
    tx.sign(signature)
    raw_tx = rlp.encode(tx)
    raw_tx_hex = w3.toHex(raw_tx)
    return w3.eth.sendRawTransaction(raw_tx_hex)


def contribute(_id, ico, eth_value):
    if get_balance(_id) >= eth_value:
        to_addr = '0x' + db.ico.find_one({'ico':ico})['address']['address']
        print(to_addr)
        signature = '0x' + db.user.find_one({'id':_id})['deposit_addr']['private']
        print(signature)
        from_addr = '0x' + db.user.find_one({'id':_id})['deposit_addr']['address']
        print(from_addr)
        return tx(from_addr, to_addr, signature, eth_value)
    else:
        return False


# In[87]:


def get_deposit_addr(_id):
    return '0x' + db.user.find_one({'id':_id})['deposit_addr']['address']


# In[88]:


def add_expert(addr):
    if db.expert.find_one({'name': 'expert_wallet'}) == None:
        if validation.is_0x_prefixed(addr) and validation.is_address(addr) and len(addr) == 42:
            return db.expert.insert_one({'name':'expert_wallet', 'addr': addr})
        else:
            return False
    else:
        return False


# In[89]:


def update_expert(addr):
    if validation.is_0x_prefixed(addr) and validation.is_address(addr) and len(addr) == 42:
        return db.expert.update_one({'name': 'expert_wallet'}, {'$set':{'addr': addr}})
    else:
        return False


# In[90]:


def get_expert(_id, length):
    signature = '0x' + db.user.find_one({'id':_id})['deposit_addr']['private']
    from_addr = '0x' + db.user.find_one({'id':_id})['deposit_addr']['address']
    
    to_addr = db.expert.find_one({'name':'expert_wallet'})['addr']
    
    if length == 'month':
        eth_value = 0.3
        time = str(datetime.date.today() + datetime.timedelta(days=31))
    elif length == '3month':
        eth_value = 0.7
        time = str(datetime.date.today() + datetime.timedelta(days=93))
    elif length == 'year':
        eth_value = 1.5
        time = str(datetime.date.today() + datetime.timedelta(days=365))
    elif length == 'forever':
        eth_value = 2.5
        time = 'forever'
        
    if get_balance(_id) >= eth_value:
        db.user.update_one({'id':_id}, {'$set':{'is_expert': time}})
        return tx(from_addr, to_addr, signature, eth_value)
    else:
        return False


# In[134]:


def get_ico_money(ico):
    return w3.eth.getBalance('0x' + db.ico.find_one({'ico':ico})['address']['address'])/10000000000000000000


# In[110]:


def transfer_from_ico(ico, to_addr, eth_value):
    signature = '0x' + db.ico.find_one({'ico':ico})['address']['private']
    from_addr = '0x' + db.ico.find_one({'ico':ico})['address']['address']
    return tx(from_addr, to_addr, signature, eth_value)

