
from WindPy import *
from datetime import *

par_list = "pre_close","open","high","low","close","volume","amt","dealnum"

#full value set
#w.wsd("600518.SH", "pre_close,open,high,low,close,volume,amt,dealnum,chg,pct_chg,swing,vwap,adjfactor,close2,turn,free_turn,oi,oi_chg,trade_status,susp_reason,mf_amt,mf_vol,mf_amt_ratio,mf_vol_ratio,mf_amt_close,mf_amt_open,ev,pe_ttm,val_pe_deducted_ttm,pb_lf,ps_ttm", "2009-03-19", "2016-09-24", "adjDate=0")

#only update key values for demo only
#win_data=w.wsd(stock_name, "pre_close,open,high,low,close,volume,amt,dealnum", "2009-03-19", datetime.today(), "adjDate=0")

def get_par_string():
    par_string = par_list[0]
    
    if len(par_list)<2:
        return par_string
    
    for i in range(len(par_list)-1):
        par_string = par_string+","+ par_list[i+1]

    return par_string


def get_history_data(stock_code,start_day,end_day=datetime.today()):	
    print ("start to query data from wind")
    par_string = get_par_string()
    print(par_string)
    wind_data = w.wsd(stock_code, par_string, start_day, end_day, "adjDate=0")
	
    print("Data query finished, %d record be found" %len(wind_data.Data[0]))
    return wind_data

def connect_to_wind():
    w.start()
    print("wind connection is:", end="")
    print(w.isconnected()) 
    
def disconnect_to_wind():
    #w.disconnect()
    print("wind connection has been closed")	