# -*- coding:utf-8 -*-
# Author:harry
# Editdate:2016-09-25

from GetStockHistory_wind import *
from SaveData_mdb import *
from datetime import *


#start wind
stock_name = "600518.SH"

#read data
connect_to_wind()
wind_data = get_history_data(stock_name,"2016-01-01")
disconnect_to_wind()

#write data
#save_data_to_mdb(wind_data)
