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
            eval("self.{}".format(args.policy))
    
    def strate1(self):
        st = strategy1.strate()
        stock_data = st.import_data('150023.SZ','2010-01-01','2015-04-23')
        # �жϽ��������Ƿ�����Ҫ��
        if not st.stock_trading_days(stock_data, trading_days=500):sys.exit()
        st.strategy3_sczbA50(stock_data)
        st.account(stock_data)
        # ѡȡʱ���
        return_data = st.select_date_range(stock_data, start_date = pd.to_datetime('20060101'), trading_days=250)
        return_data['capital'] = (return_data['capital_rtn'] + 1).cumprod()
        # =====���ݲ��Խ��,��������ָ��
        # �������250��Ĺ�Ʊ,�����ۼ��ǵ���.�Լ�ÿ�꣨�£��ܣ���Ʊ�Ͳ�������
        st.period_return(return_data, days=250, if_print=True)
        # ����ÿ�������Ľ��,�������ָ��
        st.trade_describe(stock_data)
        # =====�����ʽ�����,�����������ָ��
        st.Strategyperformance()
    
    
if __name__ == '__main__':
    m = main()
    args = m.parseargs()
    print(args)
    m.action(args)
    
    
    
    
    
    
    
    
    
    