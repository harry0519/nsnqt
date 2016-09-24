# -*- coding:utf-8 -*-
# Author:harry
# Editdate:2016-09-1
# example to show how to get history data from wind
from WindPy import *
from datetime import *
import csv
#from pymongo import MongoClient

#start wind
stock_name = "600518.SH"
file_type  = ".csv"
w.start()
print("wind connection is:", end="")
print(w.isconnected())
	
print ("start to query data from wind")

#full value set
#w.wsd("600518.SH", "pre_close,open,high,low,close,volume,amt,dealnum,chg,pct_chg,swing,vwap,adjfactor,close2,turn,free_turn,oi,oi_chg,trade_status,susp_reason,mf_amt,mf_vol,mf_amt_ratio,mf_vol_ratio,mf_amt_close,mf_amt_open,ev,pe_ttm,val_pe_deducted_ttm,pb_lf,ps_ttm", "2009-03-19", "2016-09-24", "adjDate=0")

#only update key values for demo only
#win_data=w.wsd(stock_name, "pre_close,open,high,low,close,volume,amt,dealnum", "2009-03-19", datetime.today(), "adjDate=0")
win_data=w.wsd(stock_name, "pre_close,open,high,low,close,volume,amt,dealnum", "2016-01-01", datetime.today(), "adjDate=0")
print ("query data from win done")
print (win_data.Data)

#####################################################################################################
with open(stock_name + file_type,"w",newline="") as datacsv:
	csvwriter = csv.writer(datacsv,dialect = ("excel"))
	csvwriter.writerow(win_data.Data)
  
print ("print to" + stock_name + file_type +"done")

