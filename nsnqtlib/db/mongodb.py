# -*- coding:utf-8 -*-
# Author:harry
# Editdate:2016-10-05

from pymongo import MongoClient
import fields

server_ip = "127.0.0.1"
server_port = 27017

usr_name = "root"
usr_pwd  = "nsnqt"
ali_ip   = "114.55.53.68"

def connect_to_mdb(ip="localhost", port=27017):
    server_ip = ip
    server_port = port
    #db_client = MongoClient(server_ip, server_port)
    #print("connected to "+ip)
    return db_client

def connect_to_remote():
    server_ip = ali_ip
    server_port = 27017
    db_client = MongoClient(server_ip, server_port)   
    
    db_client.admin.authenticate("root","nsnqt")                   #test数据库用户名和密码验证

    return db_client
        
def disconnect_to_mdb(db_client):
    #db_client.disconnect()
    print("disconnected")
        
def save_future_data_to_mdb(data_set,table_map,table_name):
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

def save_stock_data_to_mdb(data_set,table_name):
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
    
def save_fund_data_to_mdb(data_set,table_name):
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
    
def create_db_to_mdb(data_set,db_name,table_name):
    print(db_name+table_name)
           
def get_data_from_mdb(sql):
    print(sql)