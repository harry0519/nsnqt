# -*- coding:utf-8 -*-
# Author:harry
# Editdate:2016-09-1
# example to show how to get history data from wind
from WindPy import *
from datetime import *
import csv
from pymongo import MongoClient

#start wind
w.start()
print(w.isconnected())



#��������ָ�� HSCEI.HI
#pre_close     	, ǰ���̼� 0
#open          	, �ɿ��̼� 1
#high          	, ��߼� 2
#low			, ��ͼ� 3
#close			, ���̼� 4
#volume			, ������ 5
#amt			, �����ܼ� 6
#turn			, �������� 7
#pe_ttm			, PE 8
#pb_lf			, PB 9
			
print ("start to query HSCEI.HI")

wset_listed_stocks = w.wsd("HSCEI.HI", "pre_close,open,high,low,close,volume,amt,turn,pe_ttm,pb_lf", "1994-09-01", datetime.today(), "TradingCalendar=HKEX;Currency=CNY")

w.stop()
print("query data done")

print("start to save to database")
client = MongoClient("localhost", 27017)    #�������ݿ������
db = client.hk_index               			#��ȡ���ݿ�����


print(datetime.today())
#####################################################################################################


for j in range(len(wset_listed_stocks.Data[0])):
    db.hscei_hi.update_one({"date":wset_listed_stocks.Times[j]},
        {"$set":{ 
            "pre_close":wset_listed_stocks.Data[0][j],
            "open":wset_listed_stocks.Data[1][j],
            "high":wset_listed_stocks.Data[2][j],
            "low":wset_listed_stocks.Data[3][j],
            "close":wset_listed_stocks.Data[4][j],
            "volume":wset_listed_stocks.Data[5][j],
            "amt":wset_listed_stocks.Data[6][j],
            "turn":wset_listed_stocks.Data[7][j],
            "pe_ttm":wset_listed_stocks.Data[8][j],
            "pb_lf":wset_listed_stocks.Data[9][j] }}, upsert=True)   



print ("save to database done")