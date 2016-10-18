# -*- coding:utf-8 -*-
import argparse
import sys

from nsnqtlib.servers import serverlist
from nsnqtlib.db import mongodb

class windbupdate():
    def __init__(self):
        pass

    #process action to get data for different market
    def update_security(self,args):
    	print("security updated")
    def update_future(self,args):
    	print("future updated")
    def update_fund(self,args):
    	print("fund updated")
    def update_index(self,args):
    	print("index updated")
    def update_currency(self,args):
    	print("currency updated")

    def parseargs(self):
        parser = argparse.ArgumentParser() 
        
        action_list=["security","future","fund", "index", "currency"]
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
        
        if action == "security":
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
    args = wind.parseargs()
    print(args)
    for item in args.action:
        wind.action(item,args)
    
       
    
    


