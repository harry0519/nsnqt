
import sys, getopt

import numpy as np
import pandas as pd
import datetime as dt

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import calendar
import random
import tushare as ts

from nsnqtlib.db.mongodb import MongoDB
from nsnqtlib.config import DB_SERVER,DB_PORT,USER,PWD,AUTHDBNAME

#基于交易记录进行策略测试
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
                 Sharpe_thres=0.5, AnnualReturn_thres=0.2, MDD_thres=0.2,\
                 SuccessRatio_thres = 0.7,
                 Accurate_metrics = True, Fixed_fee=0.002, Chart_display=False,\
                 Chart_save = False):
        self.principal = principal
        self.trade_history = trade_history
        self.sharpe_thres = Sharpe_thres
        self.annualreturn_thres = AnnualReturn_thres
        self.MDD_thres = MDD_thres
        self.successratio_thres = SuccessRatio_thres
        self.final_value = 0
        self.total_commission = 0
        self.accurate_metrics = Accurate_metrics
        self.fixed_fee = Fixed_fee
        self.chart_display = Chart_display
        self.chart_save = Chart_save
        self.df = trade_history[["stock","buy_date","sell_date","holddays","profit","buy_money"]]
        self.start_date = min(dt.datetime.strptime(i, "%Y-%m-%d") for i in self.df["buy_date"].values)
        self.end_date = max(dt.datetime.strptime(i, "%Y-%m-%d") for i in self.df["sell_date"].values)
        '''
        self.etf300 = ts.get_hist_data('hs300',start='2016-10-06')#[['p_change']]
        print(self.etf300)
        print(self.etf300.loc['2016-10-31',['p_change']].values[0])
        '''
        '''
        self.m = MongoDB(DB_SERVER,DB_PORT,USER,PWD,AUTHDBNAME)
        self.formatlist = ["date","volume","close","high","low","open","pre_close"]
        self.buy_ind = []
        self.sell_ind = []
        #self._getETF300()
        '''
        if self.accurate_metrics:
            self._getTradeStockData()
        return
        
    def _getdata(self,trade_date,collection="000923.SZ",
                 db="ml_security_table",\
                 out=[],isfilt=True,filt={}):
        if not out:out = self.formatlist
        if isfilt and not filt: filt =  \
            {"date":{"$gt": trade_date, "$lt": trade_date+dt.timedelta(days=1)}}
        query = self.m.read_data(db,collection,filt=filt)
        return self.formatquery(query,out)
       
    def formatquery(self,query,out):
        '''
        query:your source data ,should be a list with dict
        out:the fields you want to convert into dataframe 
        '''
        if not out:
            query = [i for i in query.sort("date", 1)]
        else:
            query = [{k:i[k] for k in out} for i in query.sort("date", 1)]
        return pd.DataFrame(query)
    
    #初始化时获得交易股票对应的指标和价格
    def _getTradeStockData(self):
        for i in self.df.values:
            buy = self._getdata(dt.datetime.strptime(i[1], "%Y-%m-%d"),collection=i[0])
            sell = self._getdata(dt.datetime.strptime(i[2], "%Y-%m-%d"),collection=i[0])
            #目前按照一天同一支股票只有一个记录计算，后续如果一天多个记录，这里需要调整
            self.buy_ind.append(buy[self.formatlist].values[0].tolist())
            self.sell_ind.append(sell[self.formatlist].values[0].tolist())
        #use index as list index to find correspond buy & sell data
        self.df["index"]=self.df.index.tolist()
        return
        
    #初始化时获得ETF300对应的指标和价格
    #仅有2005年后的数据，使用之前的数据可能会报错
    def _getETF300(self):
        print("Start: -----Use ETF300 as baseline-----")
        filt = {"date":{"$gt": self.start_date, "$lt": self.end_date+dt.timedelta(days=1)}}
        ETF300 = self._getdata("",collection="000300.SH", filt=filt)
        

        return


    def GeneralTest(self):
        print("Start: -----General Test-----")
        warning = False
        #买入点涨停/涨幅超过9.8%
        #卖出点跌停
        
        #交易当日无成交或者一字板
        for i in range(len(self.buy_ind)):
            #当日无成交
            if int(self.buy_ind[i][1]) == 0:
                print("Warning: Volumn in buy in date is 0!!")
                warning = True
            #一字板
            if round(self.buy_ind[i][3],6) == round(self.buy_ind[i][4],6):
                print("Warning: Word one board during buy!!")
                warning = True
            if warning == True:
                fail_stock = self.df.iloc[[i]].values
                print("Stock:%s, buy in date %s."%(fail_stock[0][0],fail_stock[0][1]))
                warning = False
                
        for i in range(len(self.sell_ind)):
            #当日无成交
            if int(self.sell_ind[i][1]) == 0:
                print("Warning: Volumn in sell out date is 0!!")
                warning = True
            #一字板
            if round(self.sell_ind[i][3],6) == round(self.sell_ind[i][4],6):
                print("Warning: Word one board during sell !!")
                warning = True
            if warning == True:
                fail_stock = self.df.iloc[[i]].values
                print("Stock:%s, sell out date %s."%(fail_stock[0][0],fail_stock[0][2]))
                warning = False
        return
    
    def AbnormalTest(self):
        #Just warning print，but no impact to test result
        print("Start: -----Abnormal Check-----")
        #买入时跌停
        
        #卖出时涨停
        
        return
    
    def BuyPointTest(self):
        '''
        '''
        print("Start: -----Buy point Test-----")
        
        
        
        return
    
    def SellPointTest(self):
        '''
        '''
        print("Start: -----Sell point Test-----")
        
        return
    
    #策略有效/正确性测试 -- 功能测试
    def ValidityTest(self):
        
        self.BuyPointTest()
        self.SellPointTest()
        self.GeneralTest()
        self.AbnormalTest()

        return
    
    #买入成功率：买点涨的概率
    def SuccessRatio(self):
        sucess = 0
        for i in self.df.values:
            if i[4] > 0:
                sucess +=1
        sucess_ratio = sucess/len(self.df)
        return sucess_ratio
    
    # 夏普比率： 平均收益率/收益率标准差
    #Sharpe Ratio: Sharpe ratio = Excess return / Standard deviation
    #input: 
    #    erp: Portfolio expected return rate 
    #         within fixed timeperiod (e.g.yearly/monthly) 
    #    rf: risk-free/expect rate of interest  
    def Sharpe(self, erp=[], rf=0.039):
        a = np.array(erp)
        sharpe = (np.mean(a)-rf)/np.std(a,ddof=1)
        return sharpe
        
    #单次最大收益
    def MaxSingleEarn(self):
        return self.df["profit"].max()
    
    #单次最大亏损
    def MaxSingleLoss(self):
        return self.df["profit"].min()
    
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
    def AnnualReturn(self):
        final_return = self.final_value/self.principal
        years = (self.end_date - self.start_date).days/365.25
        return np.power(final_return, 1/years)-1, final_return-1, years
    
    #日净值历史
    def daily_accumulated(self):
        '''
        '''
        datelist = [i.strftime('%Y-%m-%d') for i in pd.date_range(self.start_date, self.end_date)]
        trade_history = {d:{'buy':[],'sell':[]} for d in datelist}
        total_money = {d:0 for d in datelist}
        hold_list = []
        #用于存储交易日数据，以计算非交易日的净值
        #{stock:[]}
        current_price = {}

        #To be added: 按每支股票每天的收盘价计算净值

        #To be added: 增加以大盘指数为baseline做对比图

        for i in self.df.values:
            trade_i = i.tolist()
            buydate = trade_i[1]
            selldate = trade_i[2]
            trade_history[dt.datetime.strptime(buydate,"%Y-%m-%d").strftime("%Y-%m-%d")]['buy'].append(trade_i)
            trade_history[dt.datetime.strptime(selldate,"%Y-%m-%d").strftime("%Y-%m-%d")]['sell'].append(trade_i)
        
        #现金流初始化
        current = self.principal
        #模拟交易开始
        for date in datelist:
            #print(date)
            if len(trade_history[date]) > 0:
                for buy_stock in trade_history[date]['buy']:
                    current -= buy_stock[5]
                    hold_list.append(buy_stock)
                    if round(current,6) < 0:
                        print("Error: Buy %.20f exceed, left %.20f:"%(buy_stock[5],current))
                        print(buy_stock)
                for sell_stock in trade_history[date]['sell']:
                    current += sell_stock[5]*(1+sell_stock[4])*(1-self.fixed_fee)
                    self.total_commission += sell_stock[5]*(1+sell_stock[4])*self.fixed_fee
                    hold_list.remove(sell_stock)
            #计算净值： 现金流+股票净值(以收盘价计算)
            total_money[date] = current
            for hold_stock in hold_list:
                stock = self._getdata(dt.datetime.strptime(date, "%Y-%m-%d"),\
                                      collection=hold_stock[0])
                if not(stock.empty):
                    stockl = stock[self.formatlist].values[0].tolist()
                    current_price[hold_stock[0]] = stockl
                
                #print("现金流："+str(current))
                total_money[date] +=  hold_stock[5]/self.buy_ind[hold_stock[6]][2]*\
                                        current_price[hold_stock[0]][2]
            '''
                print(hold_stock[0])
                print("买入金额"+str(hold_stock[5])+"_买入价"+str(self.buy_ind[hold_stock[6]][2])+"_当前价"+str(stockl[2]))
            print("当前总金额："+str(total_money[date]))
            '''
        #最终结果，用于收益率计算      
        self.final_value = current
        
        if(self.chart_display or self.chart_save):  
            print("Chart: -----Daily value chart-----")
            newdf = pd.DataFrame(data=[total_money[i] for i in datelist], \
                                   index=datelist,columns=["totalmoney"])
            newdf["date"] = newdf.index
            newdf.plot(x="date", y="totalmoney", kind='area')
        if self.chart_display:
            plt.show()
        if self.chart_save:
            plt.savefig("daily_money.png")
        
        return total_money

    #没有考虑日价格波动数据的方式用这个函数来测量
    #优势：速度快，不用读数据库
    #可能会有些波动性误差
    def daily_accumulated_fuzzy(self):
        '''
        '''
        datelist = [i.strftime('%Y-%m-%d') for i in pd.date_range(self.start_date, self.end_date)]
        sell_history = {d:[] for d in datelist}
        current_money = {d:0 for d in datelist}
    
        for i in self.df.values:
            selldate = i[2]
            sell_history[dt.datetime.strptime(selldate,"%Y-%m-%d").strftime("%Y-%m-%d")].append(i)
            
        current = self.principal
        for date in datelist:
            if len(sell_history[date]) > 0:
                for sell_stock in sell_history[date]:
                    commission = sell_stock[5]*(1+sell_stock[4])*self.fixed_fee
                    current = current + sell_stock[4]*sell_stock[5] - commission
                    self.total_commission += commission
            current_money[date] = current
            

            '''
            try:
                print(date)
                print(self.etf300.loc[date,['p_change']].values[0])
            except:
                pass
            '''
    
        #最终结果，用于收益率计算      
        self.final_value = current
        
        if(self.chart_display or self.chart_save):
            print("Chart: -----Daily value chart-----")
            newdf = pd.DataFrame(data=[current_money[i] for i in datelist], \
                                       index=datelist,columns=["totalmoney"])
            newdf["date"] = newdf.index
            newdf.plot(x="date", y="totalmoney", kind='area')
        if self.chart_display:
            plt.show()
        if self.chart_save:
            plt.savefig("daily_money.png")
            
        return current_money
        
    #月净值历史, 月度年化收益率
    #结算日：月末最后一天
    def monthly_accumulated(self):
        '''
        output:
            dict:{date:[total_money,growth_ratio,annual_yield]}   !!no order for dict
                  Monthly accumulated history during whole trade
        '''
        if self.accurate_metrics:
            daily = self.daily_accumulated()
        else:
            daily = self.daily_accumulated_fuzzy()
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
        
        if(self.chart_display or self.chart_save):
            print("Chart: -----Monthly value chart-----")
            newdf = pd.DataFrame(data=[monthly_money[i] for i in monthlist], \
                                       index=monthlist,columns=["totalmoney","growth","annualyield"])
            newdf["month"] = newdf.index
            newdf.plot(x="month", y="totalmoney", kind='area')
        if self.chart_display:
            plt.show()
        if self.chart_save:
            plt.savefig("monthly_money.png")

        return monthly_money
    
    #交易频度统计
    def TotalDeals(self):
        return len(self.df)
        
    #单笔交易收益率
    def ProfitHistogram(self,bins=10):
        print("Chart: -----Profit per deal chart-----")
        plt.hist(self.df["profit"].values, bins=bins, alpha=0.5)   
        plt.xlabel('value', fontsize=16)  
        plt.ylabel('count', fontsize=16)  
        plt.title('Profit for each deal' , fontsize=16)  
        plt.tick_params(axis='both', which='major', labelsize=12)
        if self.chart_display:
            plt.show()
        if self.chart_save:
            plt.savefig("Profit_per_deal_distribution.png")
        
        plt.figure(0)
        print("Chart: -----Daily profit per deal chart-----")
        daily=[]
        for i in self.df.values:
            daily_profit = i[4]/i[3]
            daily.append(daily_profit)
        df = pd.DataFrame(daily, columns=["daily"])
        plt.hist(df["daily"].values, bins=bins, alpha=0.5)   
        plt.xlabel('value', fontsize=16)  
        plt.ylabel('count', fontsize=16)
        plt.title('Daily profit distribution' , fontsize=16)
        plt.tick_params(axis='both', which='major', labelsize=12) 
        if self.chart_display:
            plt.show()
        if self.chart_save:
            plt.savefig("Profit_daily_distribution.png")
        
        
    #策略回测：收益率+指标报告
    def BackTest(self): 
        accumulated = []
        erp = []
        #收益率分布图
        if(self.chart_display or self.chart_save):
            self.ProfitHistogram()
        #收益曲线
        monthly = self.monthly_accumulated()
        month_list = sorted(monthly.keys())
        #统计结果
        for month in month_list:
            accumulated.append(monthly[month][0])
            erp.append(monthly[month][2])
        
        #checkpoints
        print("Start: -----Trade duration-----")
        print(self.start_date.strftime('Start date: %Y-%m-%d'))
        print(self.end_date.strftime('End date: %Y-%m-%d'))
        
        ar,final_return,years = self.AnnualReturn()
        result = "Fail" if ar < self.annualreturn_thres else "Pass"
        total_deals = self.TotalDeals()
        montly_deals = total_deals/years/12
        expect_return = final_return/total_deals
        print("%s: -----Profit Test-----"%result)
        print("[Result]: Initial %.2f --> %.2f within %.1f years."\
              %(self.principal,self.final_value, years))
        print("[Result]: Total commission %.2f."\
              %(self.total_commission))
        print("[Result]: Total return %.2f%%. Annual return %.2f%%"\
              %((final_return)*100, (ar)*100))
        print("[Result]: Total %d deals, monthly average %.2f deals"%(total_deals, montly_deals))
        print("[Result]: Average profit %.2f%% for each deal"%(expect_return*100))
        
        
        print("Start: -----Suceess deal Test-----")
        print("[Result]: Max single earn %.2f%%. Max single loss %.2f%%"\
              %(self.MaxSingleEarn()*100,self.MaxSingleLoss()*100))
        sr = self.SuccessRatio()
        result = "Fail" if sr < self.successratio_thres else "Pass"
        print("[Result]: Success rate is %.2f%%"%(sr*100))
        
        sharpe = self.Sharpe(erp)
        result = "Fail" if sharpe < self.sharpe_thres else "Pass"
        print("%s: -----Sharpe Rate Test-----"%result)
        print("[Result]: Sharpe rate is %.2f"%sharpe)
        
        MDD = self.MDD(accumulated)
        result = "Fail" if MDD > self.MDD_thres else "Pass"
        print("%s: -----Max Draw Down Test-----"%result)
        print("[Result]: Max Draw Down is %.2f%%"%(MDD*100))
        return
    

    def ExtremeCaseTest(self):
        print("Pass: -----Extreme Case Test-----")
        return
    
    #sharpe大于1，alpha为正，beta小于0.8的策略比较好
    #全量测试：功能测试+回测+极端测试
    def StrategyTest(self):
        if self.accurate_metrics:
            self.ValidityTest()
        self.BackTest()
        self.ExtremeCaseTest()
        return

#基于可以交易点列表模拟产生交易数据
class TradeSimulate():
    '''
    input: 
        tradable_list: stock buy-in and sell-out history. format should be
            "index(title is none)" "stock","buy_date","sell_date","holddays","profit"
            date format: %Y-%m-%d
        principal: initial invest money
    output:
        dict:{date:total_money}   !!no order for dict
              Daily accumulated history during whole trade
    '''
    
    def __init__(self, tradable_list, principal=100, piece=50):
        self.piece = piece
        self.principal = principal
        self.df = tradable_list[["stock","buy_date","sell_date","holddays","profit"]]
        self.start = sorted(self.df["buy_date"].values)[0]
        self.end = sorted(self.df["sell_date"].values)[-1]
        return
        
    def TradeSimulate(self):
        '''
        '''
        totalmoney = self.principal
        leftmoney = self.principal
        holds = []
        datelist = [i.strftime('%Y-%m-%d') for i in pd.date_range(self.start, self.end)]
        result = {d:[] for d in datelist}
        gains = {d:0 for d in datelist}
        trade_history = []

        for i in self.df.values:
            buydate = i[1]
            result[buydate].append(i)
        
        for date in datelist:
            currentholdnum = len(holds)
            current_day_could_buy_num = len(result[date])
            if current_day_could_buy_num >=1 and currentholdnum < self.piece:
                buymoney = leftmoney/(self.piece-currentholdnum)
                if current_day_could_buy_num + currentholdnum <= self.piece:
                    leftmoney = leftmoney - buymoney*current_day_could_buy_num
                    holds.extend([([j for j in i],buymoney) for i in result[date]])
                else:
                    leftmoney = 0
                    holds.extend([([j for j in i],buymoney) for i in random.sample(result[date],self.piece-currentholdnum)])
            for d in holds[:]:
                sell_date = d[0][2]
                if sell_date <= date: 
                    holds.remove(d)
                    leftmoney += d[1]*(d[0][4]+1-0.0015)  
                    totalmoney += d[1]*(d[0][4]-0.0015)
                    stock_i=d[0]
                    stock_i.append(d[1])
                    trade_history.append(stock_i)
            gains[date] = totalmoney
        
        resultdf = pd.DataFrame(trade_history,columns=["stock","buy_date","sell_date","holddays","profit","buy_money"])
        print("Report: -----Trade simulation-----")
        print("[Result]: %d piece simulat"%self.piece)
        print("[Result]: %d deals, cover %.2f%% of tradable points"%(len(resultdf),len(resultdf)/len(self.df)*100))
        
        return resultdf

def strategytesthelp():
    print("-f filename: Tradable list from your strategy")
    print("    File format should be .csv, default use macd.csv")
    print('    Content format: "index(title is none)" "stock","buy_date","sell_date","holddays","profit"')
    print("    date format: %Y-%m-%d")
    print("-h: Show help information")
    print("-s <show/save>: Show chart or save as png")
    print("-t <backtest/piecetest>: backtest -- back test;  piecetest -- (20-200)pieces test")
        
if __name__ == '__main__':
    #Buy points test
    #Sell points test
    #Regression test
    #print(ts.get_realtime_quotes('399300'))
    filename = "macd.csv"
    show_chart = "save"
    test_type = "backtest"
    opts, args = getopt.getopt(sys.argv[1:], "hf:s:t:")
    
    for op, value in opts:
        if op == "-f":
            filename = value
        elif op == "-s":
            show_chart = value
        elif op == "-t":
            test_type = value
            
        elif op == "-h":
            strategytesthelp()
            sys.exit()
   
    if test_type == "backtest":
        df = pd.read_csv(filename)
        s = TradeSimulate(df, piece=100)
        newdf = s.TradeSimulate()
        
        if show_chart == "show":
            chart_display = True
            save_chart = False
        elif show_chart == "save": 
            chart_display = False
            save_chart = True
        else:
            chart_display = save_chart = False
        a = StrategyTest(100, newdf, Accurate_metrics = False, \
                         Chart_display = chart_display, Chart_save = save_chart)
        a.BackTest()
    elif test_type == "piecetest":
        sharpe = []
        MDD = []
        Piece = []
        annual_return = []
        df = pd.read_csv(filename)
        for i in range(20,201):
            accumulated = []
            erp = []
            s = TradeSimulate(df, piece=i)
            newdf = s.TradeSimulate()
            
            a = StrategyTest(100, newdf, Accurate_metrics = False)
            #收益曲线
            monthly = a.monthly_accumulated()
            month_list = sorted(monthly.keys())
            #统计结果
            for month in month_list:
                accumulated.append(monthly[month][0])
                erp.append(monthly[month][2])
            sharpe.append(a.Sharpe(erp))
            MDD.append(a.MDD(accumulated))
            Piece.append(i)
            
            ar,final_return,years = a.AnnualReturn()
            annual_return.append(ar)
        
        chartdf = pd.DataFrame(Piece, columns=['piece'])
        chartdf.index = chartdf['piece']
        chartdf['sharpe'] = sharpe
        chartdf['MDD'] = MDD
        chartdf['annual_return'] = annual_return
        chartdf.plot(x="piece", kind='line')
        if show_chart == "show":
            plt.show()
        elif show_chart == "save":
            plt.savefig("Sharpe_MDD.png")
    else:
        print("-t error: No type available as %s"%test_type)
        strategytesthelp()
    

    
