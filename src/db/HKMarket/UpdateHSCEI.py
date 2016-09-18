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



#恒生国企指数
#wind_code/sec_code     , wind代码 0
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
print ("start to query HSCEI.HI")

wset_listed_stocks = w.wsd("HSCEI.HI", "pre_close,open,high,low,close,volume,amt,turn,pe_ttm,pb_lf", "1994-09-01", "2016-09-17", "TradingCalendar=HKEX;Currency=CNY")

print("query data done")

print("start to save to database")
client = MongoClient("localhost", 27017)    #链接数据库服务器
db = client.hk_index               			#获取数据库连接

#db.hscei_hi.insert_one({"date":wset_listed_stocks.Times[0]}) 
print(wset_listed_stocks)
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
            "pb_lf":wset_listed_stocks.Data[9][j] }})   



print ("save to database done")