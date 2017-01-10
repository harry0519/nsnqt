# -*- coding:utf-8 -*-
import argparse
import sys
import time
from time import clock
from datetime import *
import logging
import urllib.request
import re
import tushare as ts

from nsnqtlib.servers import serverlist
from nsnqtlib.db import mongodb
from nsnqtlib.utils import WindQuote
from nsnqtlib.db.fields import *
from nsnqtlib.config import DB_SERVER,DB_PORT,USER,PWD,AUTHDBNAME
from nsnqtlib.servers.serverlist import LOCAL_SERVER_IP,MONGODB_PORT_DEFAULT



dblogger = logging.getLogger()

def init_log():
    dblogger.setLevel(logging.DEBUG)

    fh = logging.FileHandler('log/dbupdate.log')   
    ch = logging.StreamHandler() 

    formatter = logging.Formatter('[%(asctime)s] %(message)s')  
    fh.setFormatter(formatter)  
    ch.setFormatter(formatter) 
    dblogger.addHandler(fh)  
    dblogger.addHandler(ch)

def stock_daily_update():
    local_wnd = WindQuote.WndQuery()        
    local_wnd.connect()
    regular_fields = local_wnd.get_par_string(par_list_stock)
    
    security_list = local_wnd.wset("listedsecuritygeneralview","sectorid=a001010100000000")
    if security_list.ErrorCode != 0:
        dblogger.error("Get listedsecuritygeneralview failed, errcode:%d" %(security_list.ErrorCode))
        return
    else:
        dblogger.error("%d stocks returned from listedsecuritygeneralview" %(len(security_list.Data[0])))

    security_list_size = len(security_list.Data[0])
    local_db = mongodb.MongoDB()
    ali_db   = mongodb.MongoDB(DB_SERVER,DB_PORT,USER,PWD,AUTHDBNAME)

    failure_count = 0
    success_count = 0
    start = clock()

    dblogger.info("==========start to update all stocks==========")    
    for j in range(security_list_size):
        stock_name = security_list.Data[0][j]

        if stock_name[0] == '3': #=='000/001,002' #=='600/601/603,602'
            #ipo_day = company_general.Data[2][j]
            #stock_data = local_wnd.get_history_data(stock_name,regular_fields, datetime.today(),datetime.today())
            today = "2017-1-6"#datetime.today() #"2017-1-3"
            stock_data = local_wnd.get_history_data(stock_name,regular_fields,today,today)

            if stock_data.ErrorCode == 0:
                local_db.save_data("ml_security_table",stock_name,par_list_stock,stock_data)
                ali_db.save_data("ml_security_table",stock_name,par_list_stock,stock_data)      
                success_count = success_count + 1
                end = clock()
                dblogger.info("%s succeeded, loop=%d[%d/%d],used %ds" %(stock_name,j,success_count,security_list_size,end-start))
            else:
                failure_count = failure_count +1
                dblogger.error("%s failed, errcode:%d" %(stock_name, stock_data.ErrorCode))

    end = clock()
    print("\nupdated %d/%d stocks, used %ds" %(success_count,security_list_size,end-start) )

def update_all_stock():
    local_wnd = WindQuote.WndQuery()        
    local_wnd.connect()
    regular_fields = local_wnd.get_par_string(par_list_stock)
    
    security_list = local_wnd.wset("listedsecuritygeneralview","sectorid=a001010100000000")
    if security_list.ErrorCode != 0:
        dblogger.error("Get listedsecuritygeneralview failed, errcode:%d" %(security_list.ErrorCode))
        return
    else:
        dblogger.error("%d stocks returned from listedsecuritygeneralview" %(len(security_list.Data[0])))

    security_list_size = len(security_list.Data[0])
    local_db = mongodb.MongoDB(ip="192.168.0.106")
    #ali_db   = mongodb.MongoDB(DB_SERVER,DB_PORT,USER,PWD,AUTHDBNAME)

    failure_count = 0
    success_count = 0
    start = clock()

    dblogger.info("==========start to update all stocks==========")    
    for j in range(security_list_size):
        stock_name = security_list.Data[0][j]
        ipo_day = security_list.Data[7][j]
        
        if stock_name[0] == '6': #=='0' #=='6'            
        
            stock_data = local_wnd.get_history_data(stock_name,regular_fields, ipo_day, "2016-12-5")

            if stock_data.ErrorCode == 0:
                local_db.save_data("ml_security_table",stock_name,par_list_stock,stock_data, True)
                #ali_db.save_data("ml_security_table",stock_name,par_list_stock,stock_data)      
                success_count = success_count + 1
                end = clock()
                dblogger.info("%s succeeded, loop=%d[%d/%d],used %ds" %(stock_name,j,success_count,security_list_size,end-start))
            else:
                failure_count = failure_count +1
                dblogger.error("%s failed, errcode:%d" %(stock_name, stock_data.ErrorCode))

    end = clock()
    print("\nupdated %d/%d stocks, used %ds" %(success_count,security_list_size,end-start) )

#-------------for validation----------
def get_wind(hwnd,stock_name,date):
    regular_fields = hwnd.get_par_string(par_list_stock)
    return hwnd.get_history_data(stock_name,regular_fields,date,date)

def get_tushare(stock_index,date):
    return ts.get_hist_data(stock_index,start=date,end=date)

# get stock real time data from sina
# source: http://www.360doc.com/content/11/0514/23/6939219_116768712.shtml
# param[0] = stock name
# param[1] = 开盘        
# param[2] = 昨日收盘
# param[3] = 当前/今日收盘
# param[4] = 最高
# param[5] = 最低
# param[6] = 竞买价（=买一）
# param[7] = 竞卖价（=卖一）
# param[8] = 成交股数（/100得到手数）
# param[9] = 成交金额（元）
# param[10] = 买一股数
# param[11] = 买一价格
# param[12] = 买二股数
# param[13] = 买二价格
# param[14] = 买三股数
# param[15] = 买三价格
# param[16] = 买四股数
# param[17] = 买四价格
# param[18] = 买五股数
# param[19] = 买五价格
# 20-29为卖1-卖5
# param[30] = 日期
# param[31] = 时间
def get_sina(stock_index,date):
    stock_name = "http://hq.sinajs.cn/list=" + stock_index
    
    # download html
    fp = urllib.request.urlopen(stock_name)
    rt_info_page = str(fp.read())
    printdebug(rt_info_page)
    
    # Parse stock data
    startChr = "b'var hq_str_" + x +"=\""
  
    stockstring = stockstring.replace(startChr,"")
    
    stock_param = stockstring.split(",")
    
    #print(stock_param[1],stock_param[2],stock_param[3],stock_param[4])
    
    # print stock key data
    lastday   = float(stock_param[2])
    currentprice= float(stock_param[3])
    changeratio = 100.0*(currentprice/lastday-1.0)
    print(x," current ="," {0:2.3f}".format(currentprice)," {0:2.3f}".format(changeratio),"%")

    fp.close()
    return [1]    
def get_eastmoney(stock_index,date):
    stock_name = "http://quote.eastmoney.com/" + market + stock_index + ".html"
def validation_test():

    #get stock full list from wind as index
    local_wnd = WindQuote.WndQuery()        
    local_wnd.connect()
    
    security_list = local_wnd.wset("listedsecuritygeneralview","sectorid=a001010100000000")
    if security_list.ErrorCode != 0:
        dblogger.error("Get listedsecuritygeneralview failed, errcode:%d" %(security_list.ErrorCode))
        return
    else:
        dblogger.error("%d stocks returned from listedsecuritygeneralview" %(len(security_list.Data[0])))

    security_list_size = len(security_list.Data[0])

    failure_count = 0
    success_count = 0
    start = clock()

    dblogger.info("==========start to test validation==========")    
    for j in range(security_list_size):
        stock_name = security_list.Data[0][j]
        stock_index = stock_name[0:6]
        today = "2016-12-16"

        wind_data    = get_wind(local_wnd,stock_name,today)
        tushare_data = get_tushare(stock_index,today)
        #compare close only
        wind_close = wind_data.Data[4][0]
        ts_close_ar = tushare_data['close'].values
        if len(ts_close_ar) == 0:
            ts_close = 0
        else:
            ts_close = ts_close_ar[0]        

        if wind_close == ts_close:
            success_count = success_count+1
            print("%5.2f, %5.2f,%s matched(%d/%d)" %(wind_close, ts_close,stock_index,j,security_list_size))
        else:
            failure_count= failure_count+1            
            dblogger.error("%5.2f, %5.2f,%s not matched(%d/%d)" %(wind_close, ts_close,stock_index,j,security_list_size))

    end = clock()
    print("match=%d,not match=%d, match rate=%f" %(success_count,failure_count,success_count/(success_count+failure_count)) )

def get_bond_list():
    bond_list = ["129031.SZ","128013.SZ","128012.SZ","128011.SZ","128010.SZ","128009.SZ","128008.SZ","128007.SZ","128006.SZ",\
                 "128005.SZ","128004.SZ","128003.SZ","128002.SZ","128001.SZ","127003.SZ","127002.SZ","127001.SZ","126729.SZ",\
                 "125887.SZ","125731.SZ","125089.SZ","123001.SZ","120001.SZ","113501.SH","113010.SH","113009.SH","113008.SH",\
                 "113007.SH","113006.SH","113005.SH","113003.SH","113002.SH","113001.SH","110035.SH","110034.SH","110033.SH",\
                 "110032.SH","110031.SH","110030.SH","110029.SH","110028.SH","110027.SH","110025.SH","110024.SH","110022.SH",\
                 "110020.SH","110019.SH","110018.SH","110017.SH","110016.SH","110015.SH","110013.SH","110012.SH","110011.SH",\
                 "110009.SH","110007.SH","110003.SH"]
    carrydate_list=[]                 
    local_wnd = WindQuote.WndQuery()        
    hwnd = local_wnd.connect()

    for bond in bond_list:                 
        wsd = hwnd.wss(bond, "carrydate,maturitydate,paymentdate","N=0")
        #carrydate = datetime.datetime.strptime(wsd.Data[0][0], '%Y-%m-%d')
        carrydate_list.append(wsd.Data[0][0].strftime('%Y-%m-%d'))
        print(wsd.Codes[0])
    print(carrydate_list)
if __name__ == '__main__':
    init_log()
    stock_daily_update()   
    #validation_test()
    #get_bond_list()


    
    


