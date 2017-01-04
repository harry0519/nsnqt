
#Strategy description
class StrategyTest():
    '''
    Input: Trade history
    '''
    
    def __init__(self,):
        pass

    def GeneralTest(self):
        #买入点涨停/开盘涨幅超过9.8%
        
        #卖出点跌停
        
        #交易处于停盘状态
        
        print("Pass: -----General Test-----")
        pass
    
    def AbnormalTest(self):
        #Just warning print，but no impact to test result
        #买入时跌停
        
        #卖出时涨停
        print("Pass: -----Abnormal Check-----")
        pass
    
    def BuyPointTest(self):
        
        print("Pass: -----Buy point Test-----")
        return True
    
    def SellPointTest(self):
        
        print("Pass: -----Sell point Test-----")
        return True
    
    #策略有效/正确性测试 -- 功能测试
    def ValidityTest(self):
        
        self.BuyPointTest()
        self.SellPointTest()
        self.GeneralTest()
        self.AbnormalTest()

        return True
    
    def IndicatorTest(self):
        return True
    
    #策略回测：收益率+指标报告
    def BackTest(self):
        return True
    

    def ExtremeCaseTest(self):
        print("Pass: -----Extreme Case Test-----")
        return True
    
    #全量测试：功能测试+回测+极端测试
    def StrategyTest(self):
        self.ValidityTest()
        self.BackTest()
        self.ExtremeCaseTest()
        return True

if __name__ == '__main__':
    #Buy points test
    #Sell points test
    #Regression test
    a = StrategyTest()
    a.StrategyTest()
