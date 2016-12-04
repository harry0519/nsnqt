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



    #process action to get data for different market
def update_all_stock():
    local_wnd = WindQuote.WndQuery()        
    local_wnd.connect()
    regular_fields = local_wnd.get_par_string(par_list_stock)
    
    security_list = local_wnd.wset("listedsecuritygeneralview","sectorid=a001010100000000")
    if security_list.ErrorCode != 0:
        print("get list failed:%d" %(security_list.ErrorCode))
        return
    else:
        print("%d stocks listed" %(len(security_list.Data[0])))

    security_list_size = len(security_list.Data[0])
    local_db = mongodb.MongoDB()
    ali_db   = mongodb.MongoDB(DB_SERVER,DB_PORT,USER,PWD,AUTHDBNAME)

    failure_count = 0
    success_count = 0
    start = clock()
    timestamp =  time.strftime("%H:%M:%S",time.localtime(time.time()))   
    print("[%s]start to fix stocks" %(timestamp)) 

    print("==========start to update all stocks==========")    
    for j in range(security_list_size):
        stock_name = security_list.Data[0][j]
        if stock_name[0] == '0': #=='3' #=='6'
            stock_data = local_wnd.get_history_data(stock_name,regular_fields, "2016-12-02","2016-12-02")

            if stock_data.ErrorCode == 0:
                local_db.save_data("ml_security_table",stock_name,par_list_stock,stock_data)
                ali_db.save_data("ml_security_table",stock_name,par_list_stock,stock_data)      
                success_count = success_count + 1
                end = clock()
                print("%s success, loop=%d[%d/%d],used %ds" %(stock_name, j,success_count,security_list_size,end-start))
            else:
                failure_count = failure_count +1
                print("%s failed:%d" %(stock_name, stock_data.ErrorCode))

    end = clock()
    print("\nupdated %d/%d stocks, used %ds" %(success_count,security_list_size,end-start) )


if __name__ == '__main__':
    update_all_stock()   

    
    


