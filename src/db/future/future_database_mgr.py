# -*- coding:utf-8 -*-
# Author:harry
# Editdate:2016-10-05

from queryfwind import *
from save2mdb import *
from datetime import *

def internal_init():
    connect_to_wind()
    connect_to_mdb()
   
def internal_uninit():
    disconnect_to_mdb()
    disconnect_to_wind()
    
def update_cf(future_start_date):
    history_type = 2
    wind_data = []
    cf_name = ["CF00.CZC","CF01.CZC","CF02.CZC","CF03.CZC","CF04.CZC","CF05.CZC"]
    table_map = {"CF00.CZC":db.cf00,"CF01.CZC":db.cf01,"CF02.CZC":db.cf02,"CF03.CZC":db.cf03,"CF04.CZC":db.cf04,"CF05.CZC":db.cf05}
    
    for i in cf_name:
        future_data = get_history_data(i,history_type,future_start_date)
        wind_data.append(future_data)
        save_future_data_to_mdb(db_client, future_data,table_map,i)


#read future data
def create_future_database():
    
    # init connection to data source and database
    internal_init()
    
    # create cotton database
    future_start_date = "2004-06-01"
    update_cf(future_start_date)

    # create sugar database
    # create z database
    # ...
    
    # uninit all to release resource
    internal_uninit()
    
    
def update_future_database():
    # init connection to data source and database
    internal_init()

    # update last 30 days cotton trade data
    future_start_date = datetime.today() + datetime.dimedelta(days=-30)
    update_cf(future_start_date)

    # uninit all to release resource
    internal_uninit()
         
if __name__ == "__main__":
    print("start")
    create_future_database()
    