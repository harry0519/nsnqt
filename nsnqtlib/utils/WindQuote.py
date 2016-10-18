from WindPy import *
from datetime import *

par_list_stock  = "pre_close","open","high","low","close","volume","amt","dealnum"
par_list_future = "pre_close","open","high","low","close","volume","amt","oi"#,"prc_chg"

class WndQuery(object):
    par_list = ""

    def __init__(self):
        pass

    def connect(self):
        w.start() #waitTime=120 by default
        print("Wind online:", w.isconnected())
        
        return w.isconnected()
        
    def disconnect(self):
        # wind will call stop() automatically
        # w.stop()
        print("wind has been stopped")        
    
    def get_par_string(self,par_list):
        par_string = par_list[0]
        
        if len(par_list)<2:
            return par_string
        
        for i in range(len(par_list)-1):
            par_string = par_string+","+ par_list[i+1]

        return par_string

    # query history data from wind
    # type: 1=stock, 2=future
    def get_history_data(self,stock_code,search_type,start_day,end_day=datetime.today()):    

        print ("start to query data from wind")
        par_list = ""
        if search_type == 1:
            par_list = par_list_stock
        elif search_type == 2:
            par_list = par_list_future
        else:
            par_list = ""
        par_string = get_par_string(par_list)
        print(stock_code+","+par_string)
        
        wind_data = w.wsd(stock_code, par_string, start_day, end_day, "TradingCalendar=CZCE")

        print("Data query finished, %d record be found" %len(wind_data.Data[0]))
        return wind_data

    def wset(self, view_name,sector_id):
        return w.wset(view_name,sector_id)