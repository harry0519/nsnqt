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



#ȡȫ��A �ɹ�Ʊ���롢������Ϣ
#wind_code/sec_code     , wind���� 0
#sec_name               , ��Ʊ������ 1
#close_price            , �������̼� 2
#total_market_value	    , ����ֵ 3
#mkt_cap_float			, ������ֵ 4
#trade_status			, ����״̬ 5
#last_trade_day			, �������̼����� 6
#ipo_day				, �������� 7
#province				, ʡ�� 8
#sec_type				, ֤ȯ���� 9
#listing_board			, ���а� 10
#exchange				, ���н����� 11				
print ("start to query all mainland stock list")

wset_listed_stocks=w.wset("listedsecuritygeneralview","sectorid=a001010100000000")

client = MongoClient("localhost", 27017)    #�������ݿ������
#client.ml_security_table                    #test���ݿ��û�����������֤
db = client.ml_security_table               #��ȡ���ݿ�����

#####################################################################################################
for j in range(len(wset_listed_stocks.Data[0])):
    db.stock.update_one({"sec_code":wset_listed_stocks.Data[0][j]},
        {"$set":{
            "sec_name":wset_listed_stocks.Data[1][j],
            "close_price":wset_listed_stocks.Data[2][j],
            "total_market_value":wset_listed_stocks.Data[3][j],
            "mkt_cap_float":wset_listed_stocks.Data[4][j],
            "trade_status":wset_listed_stocks.Data[5][j],
            "last_trade_day":wset_listed_stocks.Data[6][j],
            "ipo_day":wset_listed_stocks.Data[7][j],
            "province":wset_listed_stocks.Data[8][j],
            "sec_type":wset_listed_stocks.Data[9][j],
            "listing_board":wset_listed_stocks.Data[10][j],
            "exchange":wset_listed_stocks.Data[11][j] }})   

  

print ("query data from win done")