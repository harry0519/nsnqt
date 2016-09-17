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



#取全部A 股股票代码、名称信息
#wind_code              , wind代码 0
#sec_name               , 股票中文名 1
#close_price            , 最新收盘价 2
#total_market_value	    , 总市值 3
#mkt_cap_float			, 流动市值 4
#trade_status			, 交易状态 5
#last_trade_day			, 最新收盘价日期 6
#ipo_day				, 上市日期 7
#province				, 省份 8
#sec_type				, 证券类型 9
#listing_board			, 上市板 10
#exchange				, 上市交易所 11				
print ("start to query all mainland stock list")

wset_listed_stocks=w.wset("listedsecuritygeneralview","sectorid=a001010100000000")
print(wset_listed_stocks)
with open("win_code.csv","w",newline="") as datacsv:
    csvwriter = csv.writer(datacsv,dialect = ("excel"))
    csvwriter.writerow(wset_listed_stocks.Data[0])
    
with open("sec_name.csv","w",newline="") as datacsv:
    csvwriter = csv.writer(datacsv,dialect = ("excel"))
    csvwriter.writerow(wset_listed_stocks.Data[1])    
    
with open("ipo_day.csv","w",newline="") as datacsv:
    csvwriter = csv.writer(datacsv,dialect = ("excel"))
    csvwriter.writerow(wset_listed_stocks.Data[7])  
    
client = MongoClient("localhost", 27017)    #链接数据库服务器
client.ml_security_table                    #test数据库用户名和密码验证
db = client.ml_security_table               #获取test数据库连接

#####################################################################################################
for item in wset_listed_stocks.Data[0]:
    db.stock.insert_one({"sec_code":item})       #往test数据库下的stock表（collection）插入一条记录   
   

print ("query data from win done")