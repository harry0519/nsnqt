# -*- coding:utf-8 -*-
# Author:harry
# Editdate:2016-10-06
import sys
sys.path.append('..\..\common')
from QueryData_wind import *
from SaveData_mdb import *
from datetime import *

def internal_init():
    connect_to_wind()
    #connect_to_mdb()
   
def internal_uninit():
    #disconnect_to_mdb()
    disconnect_to_wind()
    
#create/recreate stock data in China mainland market A
def create_stock_database():
    
    # init connection to data source and database
    internal_init()
    
    # get all stock list from WSET
    condition = 'date='+datetime.today().strftime("%Y%m%d")+';sectorId=a001010100000000;field=wind_code'
    wsetdata  = w.wset('SectorConstituent',condition)
    print("\n----- %i stocks listed-----\n" %(len(wsetdata.Data[0])))

    # save all stocks
    for j in range(0,len(wsetdata.Data[0])):
        # 通过WSS来提取IPO时间
        wssdata=w.wss(str(wsetdata.Data[0][j]),'ipo_date')
        wsddata1 = get_history_data(str(wsetdata.Data[0][j]),1,wssdata.Data[0][0])
        
        print("stockname=%s, ipo date=%s,records=%i" %(str(wsetdata.Data[0][j]), wssdata.Data[0][0], len(wsddata1.Data[0]) ))
        
        if wsddata1.ErrorCode!=0:
            continue
        
        save_stock_data_to_mdb(wsddata1,str(wsetdata.Data[0][j]))

    # uninit all to release resource
    internal_uninit()
    
    
def update_stock_database():
    # init connection to data source and database
    internal_init()

    # update last 30 days cotton trade data
    stock_start_date = datetime.today() + datetime.dimedelta(days=-30)
    update_cf(future_start_date)

    # uninit all to release resource
    internal_uninit()
         
if __name__ == "__main__":
    print("start")
    create_stock_database()
    