# -*- coding: utf-8 -*-
import easytrader
from click.decorators import password_option

class trade():
    def __init__(self,user="04yylxsxh@163.com",password="185284",zuhe="ZH995042"):
        self.user = easytrader.use('xq')
        self.user.prepare(user=user, password=password,portfolio_code=zuhe)
    
    def getbalance(self):
        '''output:[{ 'asset_balance': '资产总值','current_balance': '当前余额','enable_balance': '可用金额','market_value': '证券市值',
                    'money_type': '币种','pre_interest': '预计利息' }]
        '''
        return self.user.balance
        
    def getposition(self):
        '''output:[{'cost_price': '摊薄成本价','current_amount': '当前数量','enable_amount': '可卖数量','income_balance': '摊薄浮动盈亏','keep_cost_price': '保本价',
                    'last_price': '最新价','market_value': '证券市值','position_str': '定位串','stock_code': '证券代码','stock_name': '证券名称'}]
        '''
        return self.user.position
    
    def getentrust(self):
        '''获取今日委托单
          output：[{'business_amount': '成交数量', 'business_price': '成交价格','entrust_amount': '委托数量','entrust_bs': '买卖方向','entrust_no': '委托编号','entrust_price': '委托价格',
           'entrust_status': '委托状态', 废单 / 已报   'report_time': '申报时间', 'stock_code': '证券代码', 'stock_name': '证券名称'}]
        '''
        return self.user.entrust()
    
    def buy(self,stock="600461",number=100,price=0.55):
        self.user.buy(stock, price=price, amount=number)
        
    def cancel(self,entrust,stock):
        '''entrust:委托单号
           stock：股票代码
        '''
        self.user.cancel_entrust(entrust, stock)
        
    def sell(self,stock="600461",number=100,price=0.55):
        self.user.sell(stock, price=price, amount=number)
    
    def adjust_weight(self,stock='000001',weight=10):
        self.user.adjust_weight(stock, weight)    


if __name__ == '__main__':
    pass



