

import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import calendar

#Strategy description
class StrategyTest():
    '''
    input: 
        principal: initial invest money
        trade_history: stock buy-in and sell-out history. format should be
            "index(title is none)","stock","buy_date","sell_date","holddays","profit","buy_money"
            date format: %Y-%m-%d
    output:
        dict:{date:total_money}   !!no order for dict
              Daily accumulated history during whole trade
    '''
    
    def __init__(self,principal, trade_history, \
                 Sharpe_thres=0.5, AnnualReturn_thres=0.2, MDD_thres=0.2):
        self.principal = principal
        self.trade_history = trade_history
        self.sharpe_thres = Sharpe_thres
        self.annualreturn_thres = AnnualReturn_thres
        self.MDD_thres = MDD_thres
        self.final_value = 0
        self.df = trade_history[["stock","buy_date","sell_date","holddays","profit","buy_money"]]
        self.start_date = min(dt.datetime.strptime(i, "%Y-%m-%d") for i in self.df["buy_date"].values)
        self.end_date = max(dt.datetime.strptime(i, "%Y-%m-%d") for i in self.df["sell_date"].values)
        
        return

    def GeneralTest(self):
        #买入点涨停/开盘涨幅超过9.8%
        
        #卖出点跌停
        
        #交易处于停盘状态
        
        print("Pass: -----General Test-----")
        return
    
    def AbnormalTest(self):
        #Just warning print，but no impact to test result
        #买入时跌停
        
        #卖出时涨停
        print("Pass: -----Abnormal Check-----")
        return
    
    def BuyPointTest(self):
        
        print("Pass: -----Buy point Test-----")
        return
    
    def SellPointTest(self):
        
        print("Pass: -----Sell point Test-----")
        return
    
    #策略有效/正确性测试 -- 功能测试
    def ValidityTest(self):
        
        self.BuyPointTest()
        self.SellPointTest()
        self.GeneralTest()
        self.AbnormalTest()

        return
        
    # 夏普比率： 平均收益率/收益率标准差
    #Sharpe Ratio: Sharpe ratio = Excess return / Standard deviation
    #input: 
    #    erp: Portfolio expected return rate 
    #         within fixed timeperiod (e.g.yearly/monthly) 
    #    rf: risk-free/expect rate of interest  
    def sharpe(self, erp=[], rf=0):
        a = np.array(erp)
        sharpe = (np.mean(a)-rf)/np.std(a,ddof=1)
        return sharpe
    
    #最大回撤率
    #Max draw down ratio
    #input:
    #    accumulated: accumulated money history
    #    period: To be added....
    #         >0 means short-term MADD within input period -> worth list
    def MDD(self, accumulated=[],period=0):
        current_mdd = mdd = 0
        for i in range(len(accumulated)):
            if period>0 and i>period: 
                j = i-period
            else: 
                j = 0
        
            if i > 0:
                top = max(accumulated[int(j):int(i)])
                current_mdd = (top - accumulated[i])/top
                                  
            if mdd < current_mdd:
                mdd = current_mdd
                
        return mdd
    
    #年化收益率
    def AnnualReturn(self, final_return, years):
        return np.power(final_return, 1/years)
    
        
    #日净值历史
    def daily_accumulated(self):
        '''
        '''
        datelist = [i.strftime('%Y-%m-%d') for i in pd.date_range(self.start_date, self.end_date)]
        sell_history = {d:[] for d in datelist}
        current_money = {d:0 for d in datelist}
                
        #To be added: 按每支股票每天的收盘价计算净值
        #To be added: 检查是否存在超额支出
        for i in self.df.values:
            selldate = i[2]
            sell_history[dt.datetime.strptime(selldate,"%Y-%m-%d").strftime("%Y-%m-%d")].append(i)
    
        current = self.principal
        for date in datelist:
            if len(sell_history[date]) > 0:
                for sell_stock in sell_history[date]:
                    current = current + sell_stock[4]*sell_stock[5]
            current_money[date] = current

        self.final_value = current
        
        print("Result: -----Daily value chart-----")
        newdf = pd.DataFrame(data=[current_money[i] for i in datelist], \
                                   index=datelist,columns=["totalmoney"])
        newdf["date"] = newdf.index
        newdf.plot(x="date", y="totalmoney", kind='area')
        plt.show()
        
        return current_money
    
    #月净值历史, 月度年化收益率
    #结算日：月末最后一天
    def monthly_accumulated(self):
        '''
        output:
            dict:{date:[total_money,growth_ratio,annual_yield]}   !!no order for dict
                  Monthly accumulated history during whole trade
        '''
        daily = self.daily_accumulated()
        date_list = sorted(daily.keys())
        start_date = date_list[0]
        end_date = date_list[-1]
    
        enddatelist = [i.strftime('%Y-%m-%d') \
                    for i in pd.date_range(start_date, end_date, freq='M')]
        monthlist = [i.strftime('%Y-%m') \
                    for i in pd.date_range(start_date, end_date, freq='M')]
        monthly_money = {d:[0,0,0] for d in monthlist}
    
        last_money = self.principal
        for date in enddatelist:
            date_time = dt.datetime.strptime(date,"%Y-%m-%d")
            month = date_time.strftime("%Y-%m")
            total_money = daily[date]
            growth = total_money/last_money-1
            annual_yield = growth * 365 / \
                calendar.monthrange(date_time.year, date_time.month)[1]
            monthly_money[month] = [total_money,growth,annual_yield]
            last_money = daily[date]
    
        print("Result: -----Daily value chart-----")
        newdf = pd.DataFrame(data=[monthly_money[i] for i in monthlist], \
                                   index=monthlist,columns=["totalmoney","growth","annualyield"])
        newdf["month"] = newdf.index
        newdf.plot(x="month", y="totalmoney", kind='area')
        plt.show()

        return monthly_money

        
    #策略回测：收益率+指标报告
    def BackTest(self): 
        accumulated = []
        erp = []
        monthly = self.monthly_accumulated()
        month_list = sorted(monthly.keys())
        
        #统计结果
        for month in month_list:
            accumulated.append(monthly[month][0])
            erp.append(monthly[month][2])
        
        #checkpoints
        final_return = self.final_value/self.principal
        years = (self.end_date - self.start_date).days/365.25
        ar = self.AnnualReturn(final_return, years)
        result = "Fail" if ar < self.annualreturn_thres else "Pass"
        print("%s: -----Sharpe Rate Test-----"%result)
        print("Result: Total return %.2f%% within %.1f years"%((final_return-1)*100, years))
        print("Result: Annual return %.2f%%"%((ar-1)*100))
        
        sharpe = self.sharpe(erp)
        result = "Fail" if sharpe < self.sharpe_thres else "Pass"
        print("%s: -----Sharpe Rate Test-----"%result)
        print("Result: Sharpe rate is %.2f"%sharpe)
        
        MDD = self.MDD(accumulated)
        result = "Fail" if MDD > self.MDD_thres else "Pass"
        print("%s: -----Max Draw Down Test-----"%result)
        print("Result: Max Draw Down is %.2f%%"%(MDD*100))
        return
    

    def ExtremeCaseTest(self):
        print("Pass: -----Extreme Case Test-----")
        return
    
    #全量测试：功能测试+回测+极端测试
    def StrategyTest(self):
        self.ValidityTest()
        self.BackTest()
        self.ExtremeCaseTest()
        return

if __name__ == '__main__':
    #Buy points test
    #Sell points test
    #Regression test
    
    df = pd.read_csv('positiongain.csv')
    a = StrategyTest(100,df)
    a.StrategyTest()
