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
            eval("self.{}".format(args.policy))
    
    def strate1(self):
        st = strategy1.strate()
        stock_data = st.import_data('150023.SZ','2010-01-01','2015-04-23')
        # 判断交易天数是否满足要求
        if not st.stock_trading_days(stock_data, trading_days=500):sys.exit()
        st.strategy3_sczbA50(stock_data)
        st.account(stock_data)
        # 选取时间段
        return_data = st.select_date_range(stock_data, start_date = pd.to_datetime('20060101'), trading_days=250)
        return_data['capital'] = (return_data['capital_rtn'] + 1).cumprod()
        # =====根据策略结果,计算评价指标
        # 计算最近250天的股票,策略累计涨跌幅.以及每年（月，周）股票和策略收益
        st.period_return(return_data, days=250, if_print=True)
        # 根据每次买卖的结果,计算相关指标
        st.trade_describe(stock_data)
        # =====根据资金曲线,计算相关评价指标
        st.Strategyperformance()
    
    
if __name__ == '__main__':
    m = main()
    args = m.parseargs()
    print(args)
    m.action(args)
    
    
    
    
    
    
    
    
    
    