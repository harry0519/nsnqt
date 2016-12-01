# -*- coding:utf-8 -*-
import argparse
import sys

from nsnqtlib.servers import serverlist
from nsnqtlib.db import mongodb
from nsnqtlib.utils import WindQuote
from nsnqtlib.db.fields import *
from nsnqtlib.config import DB_SERVER,DB_PORT,USER,PWD,AUTHDBNAME
from nsnqtlib.servers.serverlist import LOCAL_SERVER_IP,MONGODB_PORT_DEFAULT

class windbupdate():
    def __init__(self):
        pass

    #process action to get data for different market
    def update_security(self,args):
        local_wnd = WindQuote.WndQuery()        
        local_wnd.connect()
        regular_fields = local_wnd.get_par_string(par_list_stock)

        sh600611 = local_wnd.get_history_data("600611.SH",regular_fields, "1992-08-12") 

        local_db = mongodb.MongoDB(LOCAL_SERVER_IP,MONGODB_PORT_DEFAULT,None,None,None)
        ali_db   = mongodb.MongoDB(DB_SERVER,DB_PORT,USER,PWD,AUTHDBNAME)
        
        local_db.save_data("ml_security_table","600611",par_list_stock,sh600611)
        ali_db.save_data("ml_security_table","600611",par_list_stock,sh600611)
        

    def update_future(self,args):
        print("future updated")
    def update_fund(self,args):
        print("fund updated")
    def update_index(self,args):
        print("start to update index")
        local_wnd = WindQuote.WndQuery()        
        local_wnd.connect()
        regular_fields = local_wnd.get_par_string(par_list_stock)

        sh000001 = local_wnd.get_history_data("000001.SH",regular_fields, "1990-12-19")
        sz399001 = local_wnd.get_history_data("399001.SZ",regular_fields, "1991-04-03")

        local_db = mongodb.MongoDB()
        ali_db   = mongodb.MongoDB(DB_SERVER,DB_PORT,USER,PWD,AUTHDBNAME)

        local_db.save_data("mlindex","000001",par_list_stock,sh000001)
        local_db.save_data("mlindex","399001",par_list_stock,sz399001)
        ali_db.save_data("mlindex","399001",par_list_stock,sz399001)
        
        print("update index done")
        
    def update_currency(self,args):
        print("currency updated")
    def update_general(self,args):
        print("--------general update is running-------")
        local_wnd = WindQuote.WndQuery()
        local_wnd.connect()
        security_general = local_wnd.wset("listedsecuritygeneralview","sectorid=a001010100000000")
        company_general = local_wnd.wset("listedcompanygenerayview","sectorid=a001010100000000")
        local_wnd.disconnect()

        #####################################################################################################
        local_db = mongodb.MongoDB()
        local_db.connect()
        local_db.save_data("general","security_table",security_general,FIELD_SECURITY_GENERAL)
        local_db.save_data("general","company_table",company_general,FIELD_COMPANY_GENERAL)
        # 10.19 stop here
        db = ldb_session.general

        j = 0
        security_general_size = len(security_general.Data[0])
        sys.stdout.write("Uploading to security_general: %d/%d   \r" %(j, security_general_size ))
        
        for j in range(security_general_size):
            db.security_general.update_one({"sec_code":security_general.Data[0][j]},
                {"$set":{
                    "sec_name":security_general.Data[1][j],
                    "close_price":security_general.Data[2][j],
                    "total_market_value":security_general.Data[3][j],
                    "mkt_cap_float":security_general.Data[4][j],
                    "trade_status":security_general.Data[5][j],
                    "last_trade_day":security_general.Data[6][j],
                    "ipo_day":security_general.Data[7][j],
                    "province":security_general.Data[8][j],
                    "sec_type":security_general.Data[9][j],
                    "listing_board":security_general.Data[10][j],
                    "exchange":security_general.Data[11][j] }})   
            sys.stdout.write("Uploading to security_general: %d/%d   \r" %(j, security_general_size))
        
        j = 0
        company_general_size = len(company_general.Data[0])
        sys.stdout.write("Uploading to company_general: %d/%d   \r" %(j, company_general_size))
        
        for j in range(company_general_size):
            db.company_general.update_one({"company_name":company_general.Data[0][j]},
                {"$set":{
                    "inception_date":company_general.Data[1][j],
                    "ipo_date":company_general.Data[2][j],
                    "outstanding_shares":company_general.Data[3][j],
                    "sec_type":company_general.Data[4][j],
                    "regcapital":company_general.Data[5][j],
                    "chairman":company_general.Data[6][j],
                    "discloser":company_general.Data[7][j],
                    "address":company_general.Data[8][j],
                    "office":company_general.Data[9][j],
                    "zipcode":company_general.Data[10][j],
                    "telephone":company_general.Data[11][j],
                    "fax":company_general.Data[12][j],
                    "website":company_general.Data[12][j],
                    "comp_name_eng":company_general.Data[14][j] }})   
            sys.stdout.write("Uploading to company_general: %d/%d   \r" %(j, company_general_size))
        
        local_db.disconnect()
        #ali_db   = mongodb.MongoDB(serverlist.ALIYUN_SERVERS_IP,serverlist.ALIYUN_MONGODB_PORT,
        #    serverlist.ALIYUN_DBUSER_NAME,serverlist.ALIYUN_DB_PWD)

    def parseargs(self):
        parser = argparse.ArgumentParser() 
        
        action_list=["general","security","future","fund", "index", "currency"]
        parser.add_argument('action', type=str,nargs='*', #required=True,
                      help='Only action in {} are supported'.format(action_list))
        
        parser.add_argument("-n", "--name", type=str, 
                      dest="name", 
                      help="Name of query target. By default will query all avaible in specific market.") 
        parser.add_argument("-s", "--start", type=str, 
                      dest="start", 
                      help="Start day of query") 
        parser.add_argument("-e", "--end",type=str, 
                      dest="end", 
                      help="End day of query")

        parser.add_argument("-d", "--days", type=int, default=10, 
                      dest="days", 
                      help="Number of trading days from today need to query.Default day = 10")
        parser.add_argument('-v','--version', action='version', version='%(prog)s 0.1')
        #parser.add_argument('infile',nargs='?', type=argparse.FileType('r'),default=sys.stdin)
        
        args = parser.parse_args()        
        
        return args
    
    def action(self,action,args):
        
        if action == "general":
            self.update_general(args)            
        elif args == "security":
            self.update_security(args)
        elif args == "fund":
            self.update_fund(args)
        elif args == "future":
            self.update_future(args)
        elif args == "index":
            self.update_index(args)
        else:
            print("Action not defined. Please use -h to know supported market")
    
    
if __name__ == '__main__':
    wind = windbupdate()
    wind.update_security("")   
#    args = wind.parseargs()
#    print(args)
#    for item in args.action:
#        wind.action(item,args)
    
       
    
    


