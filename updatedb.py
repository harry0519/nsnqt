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

index_list = ["399001.SZ","399005.SZ","399006.SZ","000001.SH","000300.SH"]

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

# execute update in concurrent processes to improve performance
def update_proc(update_list, update_type,start_day=datetime.today(),end_day=datetime.today()):
     
    init_log()
    dblogger.info('[%s]Child update process started...' % (os.getpid()))

    wq = WindQuote.WndQuery()
    quote_string,quote_list = get_quote_string(update_type)
    
    update_size = len(update_list)

    #local_db = mongodb.MongoDB()
    #ali_db   = mongodb.MongoDB(DB_SERVER,DB_PORT,USER,PWD,AUTHDBNAME)
    failure_count,success_count= 0,0

    start = clock()

    for j in range(update_size):
        stock_name = update_list[j]
        
        stock_data = wq.get_history_data(stock_name,quote_string,start_day,end_day)

        if stock_data.ErrorCode == 0:
            #local_db.save_data("ml_security_table",stock_name,quote_list,stock_data)
            #ali_db.save_data("ml_security_table",stock_name,quote_list,stock_data)      
            success_count = success_count + 1
            end = clock()
            dblogger.info("[%s]%s db update succeeded, loop=%d[%d/%d],used %ds" %(os.getpid(),stock_name,j,success_count,update_size,end-start))
        else:
            failure_count = failure_count +1
            dblogger.error("[%s]%s get history data failed, errcode:%s" %(os.getpid(),stock_name, stock_data.ErrorCode))

    end = clock()
    dblogger.info("\n[%d]updated %d/%d stocks, used %ds" %(os.getpid(),success_count,update_size,end-start) )

def get_update_list():
    wq = WindQuote.WndQuery()
    update_list = wq.wset("listedsecuritygeneralview","sectorid=a001010100000000")

    if update_list.ErrorCode != 0:
        dblogger.error("get_update_list() failed, errcode:%d" %(update_list.ErrorCode))
    else:
        dblogger.error("%d stock names returned" %(len(update_list.Data[0])))

    return update_list.Data[0]

def update_one_index(wnd,localdb,remotedb,stock_name,start_day,end_day,db="ml_security_table"):
    regular_fields = wnd.get_par_string(par_list_stock)
   
    stock_data = wnd.get_history_data(stock_name,regular_fields,start_day,end_day)

    if stock_data.ErrorCode == 0:
        localdb.save_data(db,stock_name,par_list_stock,stock_data)
        remotedb.save_data(db,stock_name,par_list_stock,stock_data) 
        dblogger.error("%s update success" %(stock_name))     
    else:
        failure_count = failure_count +1
        dblogger.error("%s failed, errcode:%d" %(stock_name, stock_data.ErrorCode))

    return (stock_data.ErrorCode == 0)

def index_daily_update():
    dblogger.info("==========start to update all index==========")
    # 399001.SZ 深圳成指，1995-1-23上市，但可以反算到1991-4-3
    # 399005.SZ 中小板指，2006-1-24上市，但可以反算到2005-6-7
    # 399006.SZ 创业板指，2010-6-1
    # 000001.SH 上证综指，1991-7-15上市，但可以反算到1990-12-19
    # 000300.SH/399300.SZ 沪深300，2005-4-8上市，但可以反算到2002-1-4

    local_wnd = WindQuote.WndQuery()        
    local_wnd.connect()
    start = clock()
  
    local_db = mongodb.MongoDB()
    ali_db   = mongodb.MongoDB(DB_SERVER,DB_PORT,USER,PWD,AUTHDBNAME)

    update_one_index(local_wnd,local_db, ali_db, "399001.SZ",start_day,end_day)
    update_one_index(local_wnd,local_db, ali_db, "399005.SZ",start_day,end_day)
    update_one_index(local_wnd,local_db, ali_db, "399006.SZ",start_day,end_day)
    update_one_index(local_wnd,local_db, ali_db, "000001.SH",start_day,end_day)
    update_one_index(local_wnd,local_db, ali_db, "000300.SH",start_day,end_day)

# main update entry
def update_execution():
        
    #update stocks in multi-process
    #wind can't support more than 12 connections
    process_max = multiprocessing.cpu_count()*2
    update_list = get_update_list()
    t1 = (datetime.today()+timedelta(-14)).strftime('%Y-%m-%d')
    t2 = datetime.today()

    p = list()
    for i in range(process_max):        
        p.append( Process(target=update_proc, args=(update_list[i::process_max],"stock",t1,t2)) )
        p[i].start()

    print("%d processes launched for updating stocks" %(process_max))

    for j in range(len(p)):
        p[j].join()

    print("============All stock update done=============")
    #wait to start until all stocks process finished to avoid wind server overload
    pindex = Process(target=update_proc, args=(index_list,"stock",t1,t2))
    pindex.start()

    pindex.join()
    print("============All index update done=============")
    print("============All update done=============")

if __name__ == '__main__':    
    init_log()
    update_execution()

    
    


