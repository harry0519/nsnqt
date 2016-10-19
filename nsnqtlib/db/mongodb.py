# -*- coding:utf-8 -*-
# Author:harry
# Editdate:2016-10-05

from pymongo import MongoClient
# import nsnqtlib.db.fields
from nsnqtlib.db.base  import BaseDB
from nsnqtlib.config import DB_SERVER,DB_PORT,USER,PWD,AUTHDBNAME
 
class MongoDB(BaseDB):

    def __init__(self,ip=DB_SERVER, 
                     port=DB_PORT, 
                     user_name=USER, 
                     pwd=PWD,
                     authdb=AUTHDBNAME):
        super(MongoDB,self).__init__(ip=ip,port=port,user_name=user_name,pwd=pwd,authdb=authdb)
    
    def save_data(self, db_name, table_name, dataset, fields):
        return True

    def read_data(self, db_name, table_name, fields):
        dataset=None
        return dataset

    def save_future_data_to_mdb(self,data_set,table_map,table_name):
        print("===Start to save data to mongodb===")
        db = db_client.future
         
        for j in range(len(data_set.Data[0])):
            table_map.get(table_name).update_one({"date":data_set.Times[j]},
                {"$set":{ 
                    "pre_close":data_set.Data[0][j],
                    "open":data_set.Data[1][j],
                    "high":data_set.Data[2][j],
                    "low":data_set.Data[3][j],
                    "close":data_set.Data[4][j],
                    "volume":data_set.Data[5][j],
                    "amt":data_set.Data[6][j],
                    "oi":data_set.Data[7][j]}}, upsert=True)   
         
        print("data have been saved to mongodb")
 
    def save_stock_data_to_mdb(self,data_set,table_name):
        print("===Start to save data to mongodb===")
        db_engine = db_client = MongoClient(server_ip, server_port)
        db = db_engine.ml_security_table
         
        for j in range(len(data_set.Data[0])):
            table_set = db[table_name]
            table_set.update_one({"date":data_set.Times[j]},
                {"$set":{ 
                    "pre_close":data_set.Data[0][j],
                    "open":data_set.Data[1][j],
                    "high":data_set.Data[2][j],
                    "low":data_set.Data[3][j],
                    "close":data_set.Data[4][j],
                    "volume":data_set.Data[5][j],
                    "amt":data_set.Data[6][j],
                    "dealnum":data_set.Data[7][j]}}, upsert=True)   
         
        print("data have been saved to mongodb")
        disconnect_to_mdb(db_engine)
         
    def save_fund_data_to_mdb(self,data_set,table_name):
        print("===Start to save data to mongodb===")
        db_engine = connect_to_remote()
        db = db_engine.ml_fund_table
         
        for j in range(len(data_set.Data[0])):
            table_set = db[table_name]
            table_set.update_one({"date":data_set.Times[j]},
                {"$set":{ 
                    "pre_close":data_set.Data[0][j],
                    "open":data_set.Data[1][j],
                    "high":data_set.Data[2][j],
                    "low":data_set.Data[3][j],
                    "close":data_set.Data[4][j],
                    "volume":data_set.Data[5][j],
                    "amt":data_set.Data[6][j]}}, upsert=True)   
         
        print("data have been saved to mongodb")
        disconnect_to_mdb(db_engine)
    
m=MongoDB()
m.connect()