
# coding: utf-8

from pymongo import MongoClient
import requests
import datetime
from web3.utils import validation
import re
from phonenumbers import parse, is_valid_number
from web3 import Web3, HTTPProvider
import time
import rlp
from ethereum.transactions import Transaction


db = MongoClient('213.183.48.143').cryptobot
w3 = Web3(HTTPProvider('https://ropsten.infura.io/xSb0KCuTom59NVjS446D'))

#Initial add user to db
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
        user['operations'] = [{'timestamp' : str(datetime.datetime.now()),
                              'op':'create_user'}]
        addr_book = requests.post('https://api.blockcypher.com/v1/eth/main/addrs').json()
        addr_book['address'] = '0x' + addr_book['address']
        addr_book['private'] = '0x' + addr_book['private']
        addr_book['public'] = '0x' + addr_book['public']
        user['deposit_addr'] = addr_book
        
        return db.user.insert_one(user)

#Update user info
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

#ADMIN. Add new ICO
def create_ico(name, description):
    if name not in [item['ico'] for item in db.ico.find()]:
        addr_book = requests.post('https://api.blockcypher.com/v1/eth/main/addrs').json()
        addr_book['address'] = '0x' + addr_book['address']
        addr_book['private'] = '0x' + addr_book['private']
        addr_book['public'] = '0x' + addr_book['public']
        return db.ico.insert_one({'ico' :name, 
                      'address' : addr_book,
                      'description' : description,
                      'contributors' : [],
                             'locked':True})
    else:
        return False

#Lock/unlock ICO
def change_lock(name):
    if db.ico.find_one({'ico': name})['locked'] == False:
        print('ICO locked')
        return db.ico.update_one({'ico': name}, {'$set':{'locked': True}})
    else:
        return db.ico.update_one({'ico': name}, {'$set':{'locked': False}})
        print('ICO unlocked')

#Get balance of user internal wallet
def get_balance(_id):
    balance = w3.eth.getBalance(db.user.find_one({'id':_id})['deposit_addr']['address'])/1000000000000000000
    db.user.update_one({'id':_id}, {'$set':{'balance': balance}})
    return balance

#Base transaction model
def tx(from_addr, to_addr, signature, eth_value):
    try:
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
    except:
        return False


#Contribute to ICO from internal wallet
def contribute(_id, ico, eth_value):
    if get_balance(_id) >= eth_value:
        to_addr = db.ico.find_one({'ico':ico})['address']['address']
        signature = db.user.find_one({'id':_id})['deposit_addr']['private']
        from_addr = db.user.find_one({'id':_id})['deposit_addr']['address']
        tx_hash = tx(from_addr, to_addr, signature, eth_value)
        if tx_hash != False:
            log = db.user.find_one({'id':_id})['operations']
            log.append({'timestamp':str(datetime.datetime.now()),
                   'op': 'contribute',
                   'ico': ico,
                   'eth':eth_value,
                   'tx_hash':tx_hash})
            db.user.update_one({'id':_id}, {'$set':{'operations':log}})
        return tx_hash
    else:
        return False


#Get deposit address for user's internal wallet
def get_deposit_addr(_id):
    return db.user.find_one({'id':_id})['deposit_addr']['address']


#Initial add adress for expert chat income
def add_expert(addr):
    if db.expert.find_one({'name': 'expert_wallet'}) == None:
        return db.expert.insert_one({'name':'expert_wallet', 'addr': addr})
    else:
        return False

#Update address for expert chat income
def update_expert(addr):
    return db.expert.update_one({'name': 'expert_wallet'}, {'$set':{'addr': addr}})

#Purchase expert chat access
def get_expert(_id, length):
    signature = db.user.find_one({'id':_id})['deposit_addr']['private']
    from_addr = db.user.find_one({'id':_id})['deposit_addr']['address']
    
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
        tx_hash = tx(from_addr, to_addr, signature, eth_value)
        db.user.update_one({'id':_id}, {'$set':{'is_expert': time}})
        log = db.user.find_one({'id':_id})['operations']
        log.append({'timestamp':str(datetime.datetime.now()),
                    'op': 'expert',
                    'length':length,
                   'tx_hash':tx_hash})
        return tx_hash
    else:
        return False


#Get information on total funds raised by ICO in bot
def get_ico_money(ico):
    return w3.eth.getBalance(db.ico.find_one({'ico':ico})['address']['address'])/1000000000000000000


#Transfer funds raised from bot wallet to external one
def transfer_from_ico(ico, to_addr, eth_value):
    signature = db.ico.find_one({'ico':ico})['address']['private']
    from_addr = db.ico.find_one({'ico':ico})['address']['address']
    return tx(from_addr, to_addr, signature, eth_value)


#Get contributors with the amount for any specific ICO
def get_contributors(ico):
    contributions = []
    for user in db.user.find():
        for op in user['operations']:
            if op['op'] == "contribute" and op['ico'] == ico:
                contributions.append((user['username'], user['eth_addr'], op))
    return contributions

#Set new address for model B ICO funds
def update_modelb(eth_addr):
    return db.ico.update_one({'ico':'modelB'}, {'$set':{'address':{'address':eth_addr}}})
