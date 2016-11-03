# -*- coding:utf-8 -*-
import argparse
import sys
from nsnqtlib.strategies import strategy1
from nsnqtlib.mail import mail
from email.mime.image import MIMEImage

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
    
    def sendmail(self):
        fs = ["traderesult.txt"]
        imgs = ["capital_rtn.png"]
        content = ""
        m = mail.mail()
        for i in fs:
            with open(i) as f:
                content += f.read()
        for i in imgs:
            fp = open(i, 'rb')
            msgImage = MIMEImage(fp.read())
            fp.close()
        m.setmessage("trade result",content,msgImage=msgImage)
#         m.setmessage("trade result",content)
        m.sendmail()
        m.disconnect()
    
    def action(self,args):
        if args.action == "run":
            eval("strategy1.{}".format(args.policy))()
        if args.sendmail:
            self.sendmail()
                
    
if __name__ == '__main__':
    m = main()
    args = m.parseargs()
    print(args)
    m.action(args)
    
    
    
    
    
    
    
    
    
    