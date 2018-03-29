# coding: utf-8

# In[65]:


from pymongo import MongoClient
import requests
import datetime


# In[ ]:


db = MongoClient('213.183.48.143').cryptobot


# In[80]:


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