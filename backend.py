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
