# -*- coding:utf-8 -*-
import argparse
import sys
from policy import strategy1
import pandas as pd

class main():
    def __init__(self):
        pass
    def parseargs(self):
        parser = argparse.ArgumentParser() 
        
        action_list=["getdata","run","test"]
        parser.add_argument('action', type=str,
                        help='only action in {} are supported'.format(action_list))
        
        parser.add_argument("-c", "--collection", action="store",type=str, 
                      dest="collecton", 
                      help="collection name in mongodb") 
        parser.add_argument("-d", "--dbname", action="store",type=str, 
                      dest="dbname", 
                      help="db name in mongodb")
        parser.add_argument("-p", "--policy", action="store",type=str, 
                      dest="policy", 
                      help="policy choosed to run")
        parser.add_argument("-s", "--sendmail", action="store_true", 
                      dest="sendmail", 
                      help="send result with mail ")
        parser.add_argument('--version', action='version', version='%(prog)s 0.1')
        args = parser.parse_args()
        
        error_message = "args error,please check your input"
        if args.action not in action_list:
            print(error_message)
            parser.print_help()
            sys.exit(1)
        return args
    
    def action(self,args):
        if args.action == "run":
            eval("strategy1.{}".format(args.policy))
    
    
if __name__ == '__main__':
    m = main()
    args = m.parseargs()
    print(args)
    m.action(args)
    
    
    
    
    
    
    
    
    
    