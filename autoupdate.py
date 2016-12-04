# -*- coding:utf-8 -*-
import argparse
import sys
import time
from time import clock
import datetime

from nsnqtlib.servers import serverlist
from nsnqtlib.db import mongodb
from nsnqtlib.utils import WindQuote
from nsnqtlib.db.fields import *
from nsnqtlib.config import DB_SERVER,DB_PORT,USER,PWD,AUTHDBNAME
from nsnqtlib.servers.serverlist import LOCAL_SERVER_IP,MONGODB_PORT_DEFAULT

import logging

dblogger = logging.getLogger()

def init_log():
    dblogger.setLevel(logging.DEBUG)

    fh = logging.FileHandler('log/dbupdate.log')   
    ch = logging.StreamHandler() 

    formatter = logging.Formatter('[%(asctime)s][%(filename)s] %(message)s')  
    fh.setFormatter(formatter)  
    ch.setFormatter(formatter) 
    dblogger.addHandler(fh)  
    dblogger.addHandler(ch)

def update_all_stock(update_days):
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

        if stock_name[0] == '0': #=='3' #=='6'
            
            stock_data = local_wnd.get_history_data(stock_name,regular_fields, "2016-12-1","2016-12-2")

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

if __name__ == '__main__':
    init_log()
    update_all_stock(1)   


    
    


