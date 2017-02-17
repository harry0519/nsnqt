# -*- coding:utf-8 -*-
import sys
import time
import os
from time import clock
from datetime import datetime,date,timedelta 
import logging
from multiprocessing import Process
import threading, multiprocessing

from nsnqtlib.servers import serverlist
from nsnqtlib.db import mongodb
from nsnqtlib.utils import WindQuote
from nsnqtlib.utils.basequote import *

from nsnqtlib.config import DB_SERVER,DB_PORT,USER,PWD,AUTHDBNAME
from nsnqtlib.servers.serverlist import LOCAL_SERVER_IP,MONGODB_PORT_DEFAULT

# 399001.SZ 深圳成指，1995-1-23上市，但可以反算到1991-4-3
# 399005.SZ 中小板指，2006-1-24上市，但可以反算到2005-6-7
# 399006.SZ 创业板指，2010-6-1
# 000001.SH 上证综指，1991-7-15上市，但可以反算到1990-12-19
# 000300.SH/399300.SZ 沪深300，2005-4-8上市，但可以反算到2002-1-4
index_list = ["399001.SZ","399005.SZ","399006.SZ","000001.SH","000300.SH"]

dblogger = logging.getLogger()

wq = None

def init_log():
    dblogger.setLevel(logging.DEBUG)

    fh = logging.FileHandler('log/dbupdate.log')   
    ch = logging.StreamHandler() 

    formatter = logging.Formatter('[%(asctime)s] %(message)s')  
    fh.setFormatter(formatter)  
    ch.setFormatter(formatter) 
    dblogger.addHandler(fh)  
    dblogger.addHandler(ch)

# execute update in concurrent processes to improve performance
def update_proc(update_list, db,start_day=datetime.today(),end_day=datetime.today()):
     
    init_log()
    dblogger.info('[%s]Child update process started...' % (os.getpid()))

    wqp = WindQuote.WndQuery()

    quote_string,quote_list = get_quote_string(db)
    print("db=%s,str=%s,num=%d" %(db,quote_string,len(update_list)))

    update_size = len(update_list)

    local_db = mongodb.MongoDB()
    ali_db   = mongodb.MongoDB(DB_SERVER,DB_PORT,USER,PWD,AUTHDBNAME)
    failure_count,success_count= 0,0

    start = clock()

    for j in range(update_size):
        stock_name = update_list[j]
        
        stock_data = wqp.get_history_data(stock_name,quote_string,start_day,end_day)

        if stock_data.ErrorCode == 0:
            local_db.save_data(db,stock_name,quote_list,stock_data)
            ali_db.save_data(db,stock_name,quote_list,stock_data)      
            success_count = success_count + 1
            end = clock()
            dblogger.info("[%s]%s in %s update succeeded, loop=%d[%d/%d],used %ds" %(os.getpid(),stock_name,db,j,success_count,update_size,end-start))
        else:
            failure_count = failure_count +1
            dblogger.error("[%s]%s in %s get history data failed, errcode:%s" %(os.getpid(),stock_name, db, stock_data.ErrorCode))

    end = clock()
    dblogger.info("\n[%d]updated %d/%d stocks, used %ds" %(os.getpid(),success_count,update_size,end-start) )

def get_stock_list():    
    update_list = wq.wset("listedsecuritygeneralview","sectorid=a001010100000000")

    if update_list.ErrorCode != 0:
        dblogger.error("get_update_list() failed, errcode:%d" %(update_list.ErrorCode))
    else:
        dblogger.error("%d stock names returned" %(len(update_list.Data[0])))

    return update_list.Data[0]+index_list


'''
    w.wset("sectorconstituent","sectorid=1000009163000000") # 上证ETF
    w.wset("sectorconstituent","sectorid=1000009164000000") # 深圳ETF
    w.wset("sectorconstituent","sectorid=1000023348000000") # A,B均上市母代码
    w.wset("sectorconstituent","sectorid=1000023349000000") # A,B均上市A代码
    w.wset("sectorconstituent","sectorid=1000023350000000") # A,B军上市B代码
    w.wset("sectorconstituent","sectorid=a101020600000000") # 可转债
    
    w.wset("sectorconstituent","sectorid=a001010100000000") # 全部上市A股
    w.wset("sectorconstituent","sectorid=1000022276000000") # 全部上市美股
    w.wset("sectorconstituent","sectorid=a005010100000000") # NASDAQ 上市股票
    w.wset("sectorconstituent","sectorid=a005010200000000") # NYSE   上市股票
    w.wset("sectorconstituent","sectorid=1000006535000000") # 美国公募基金    
    
    w.wset("sectorconstituent","date=2017-02-12;sectorid=1000015512000000") # 全部国内期货合约（含已下市），463
    w.wset("sectorconstituent","sectorid=a599010101000000") # 中金所所有品种
    w.wset("sectorconstituent","sectorid=a599010201000000") # 上期所全部期货品种
    w.wset("sectorconstituent","sectorid=a599010301000000") # 大连期货交易所所有品种
    w.wset("sectorconstituent","sectorid=a599010401000000") # 郑州期货交易所所有品种
    w.wset("sectorconstituent","date=2017-02-12;sectorid=a101010706000000") #已到期可转债
    w.wset("sectorconstituent","date=2017-02-12;sectorid=a201010600000000") #货币市场基金
    #公募基金
    #基金市场类（净值），2017-2-13
    w.wset("sectorconstituent","date=2017-02-12;sectorid=1000008492000000") #全部基金（含发行中，已经到期），6357个
    w.wset("sectorconstituent","date=2017-02-12;sectorid=a201010700000000") #全部基金，5778
    w.wset("sectorconstituent","date=2017-02-12;sectorid=1000011866000000") #全部基金（除分级基金），5296
    #基金市场类（行情），2017-2-13
    w.wset("sectorconstituent","date=2017-02-12;sectorid=1000019786000000") #全部上市基金，671

    #私募基金
    w.wset("sectorconstituent","date=2017-02-12;sectorid=1000008494000000") #全部基金（含发行中，已经到期），51134
    w.wset("sectorconstituent","date=2017-02-12;sectorid=a201010700000000") #全部基金，40080
    '''

def get_etf_list():
    update_list = wq.wset("sectorconstituent","sectorid=1000009163000000").Data[1] # 上证ETF
    update_list+= wq.wset("sectorconstituent","sectorid=1000009164000000").Data[1] # 深圳ETF
    return update_list

def get_cbond_list():    
    update_list = wq.wset("sectorconstituent","sectorid=a101020600000000").Data[1] # 在交易可转债
    update_list += wq.wset("sectorconstituent","sectorid=a101010706000000").Data[1] #已到期可转债
    return update_list

def get_ab_etf_list():
    update_list  = wq.wset("sectorconstituent","sectorid=1000023348000000").Data[1] # A,B均上市 母代码
    return update_list

def get_ab_list():
    update_list  = wq.wset("sectorconstituent","sectorid=1000023349000000").Data[1] # A,B均上市 A代码    
    update_list += wq.wset("sectorconstituent","sectorid=1000023350000000").Data[1] # A,B均上市 B代码
    return update_list

def mp_update(update_list, process_num,db, start_day, end_day):
    if len(update_list) < 1:
        dblogger.warning("No records[%d] for %s update" %(len(update_list) , db))

    p = list()
    for i in range(process_num):       
        p.append( Process(target=update_proc, args=(update_list[i::process_num],db,start_day,end_day)) )
        p[i].start()

    dblogger.info("%d processes launched to update %d %s(s)" %(process_num, len(update_list),db))

    for j in range(len(p)):
        p[j].join()

    dblogger.info("============%s update done=============" %(db))

def mp_createdb(update_list, process_num,db):
    if len(update_list) < 1:
        dblogger.warning("No records[%d] for %s update" %(len(update_list) , db))

    p = list()
    for i in range(process_num):       
        p.append( Process(target=update_proc, args=(update_list[i::process_num],db,start_day,end_day)) )
        p[i].start()

    dblogger.info("%d processes launched to update %d %s(s)" %(process_num, len(update_list),db))

    for j in range(len(p)):
        p[j].join()

    dblogger.info("============%s creation done=============" %(db))


# main create entry
def create_execution():
        
    #update stocks in multi-process
    #wind can't support more than 12 connections
    process_max = multiprocessing.cpu_count()*2
    process_min = multiprocessing.cpu_count()

    t1 = datetime.today() #(datetime.today()+timedelta(-14)).strftime('%Y-%m-%d')
    t2 = datetime.today()

    #mp_update(get_stock_list(),process_max,"ml_security_table",t1,t2)

    #mp_createdb(get_etf_list()    , process_min,"etf").
    #mp_createdb(get_ab_list()     , process_max,"ab")
    #mp_createdb(get_ab_etf_list() , process_max,"ab_etf")
    mp_createdb(get_cbond_list()   , process_min,"cbond")
    #mp_createdb(get_etfus_list()    , process_min,"etf_us").
    print("============All creation done=============")


if __name__ == '__main__':    
    init_log()
    wq = WindQuote.WndQuery()
    print("main thread started")
    create_execution()

    
    


