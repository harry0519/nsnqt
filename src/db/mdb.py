# coding: utf-8
'''
Created on 2016��10��17��

@author: 04yyl
'''
import config
from pymongo import MongoClient
class mdb(object):
    '''
    Query data from mongodb on server
    '''

    def __init__(self, ip=config.dbserver,
                 port=config.dbport,
                 user=config.user,
                 password=config.pwd):
        self.ip = ip
        self.port = port
        self.user = user
        self.password = password
        self.client = self.connect()
    
    def connect(self):
        client = MongoClient(self.ip, self.port)       
        client.admin.authenticate(self.user,self.password)  
        return client
    
    def disconnect(self):
        self.client.close()

