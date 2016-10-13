# coding: utf-8
'''
Created on 2016年10月13日

@author: 04yyl
'''
from config import *
from pymongo import MongoClient

class Query():
    '''
    Query data from mongodb on server
    '''

    def __init__(self, ip=dbserver,port=dbport,user=user,password=pwd):
        self.ip = ip
        self.port = port
        self.user = user
        self.password = password
        self.client = self.connect()
    
    def connect(self):
        client = MongoClient(self.ip, self.port)       #�������ݿ������
        client.admin.authenticate(self.user,self.password)  #test���ݿ��û�����������֤
        return client
    
    def get_ml_security_table(self,collection): 
        db = self.client.ml_security_table
        return eval("db.{}".format(collection)).find()

# query = Query()
# for i in query.get_ml_security_table("stock"):
#     print(i)
        
        
        
                    
        