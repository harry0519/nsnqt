# -*- coding:utf-8 -*-
from WindPy import *
from datetime import *

"""
ErrorCode=0表示操作成功。
其他：
-40520001  未知错误 -40520002  内部错误
-40520003  系统错误 -40520004  登录失败
-40520005  无权限 -40520006  用户取消
-40520007  无数据 -40520008  超时错误      -40521010  超时错误
-40520009  本地WBOX错误 -40520010  需要内容不存在
-40520011  需要服务器不存在 -40520012  引用不存在
-40520013  其他地方登录错误 -40520014  未登录使用WIM工具，故无法登录
-40520015  连续登录失败次数过多
 
-40521001  IO操作错误 -40521002  后台服务器不可用
-40521003  网络连接失败 -40521004  请求发送失败
-40521005  数据接收失败 -40521006  网络错误
-40521007  服务器拒绝请求 -40521008  错误的应答
-40521009  数据解码失败 -40521010  网络超时
-40521011  频繁访问
 
-40522001  无合法会话 -40522002  非法数据服务
-40522003  非法请求 -40522004  万得代码语法错误
-40522005  不支持的万得代码 -40522006  指标语法错误
-40522007  不支持的指标 -40522008  指标参数语法错误
-40522009  不支持的指标参数 -40522010  日期与时间语法错误
-40522011  不支持的日期与时间 -40522012  不支持的请求参数
-40522013  数组下标越界 -40522014  重复的WQID
-40522015  请求无相应权限 -40522016  不支持的数据类型
-40522017  数据提取量超限

函数名/函数功能
---------------
wsd/wss 获取日间基本面数据、行情数据等
wset 获取变长数据集数据：指数成分、分红、ST股票等

wsi 获取分钟行情数据、支持技术指标变参
wst 获取日内买卖十档盘口快照、成交数据
wsq 获取订阅实时行情数据
EDB 获取宏观经济数据
"""

class WndQuery(object):

    def __init__(self):
        self.connect()

    def status(self):
        stat = w.isconnected()
        print("Wind online:", stat)
        return stat

    def connect(self):
        self.hwnd = w.start() #waitTime=120 by default
        return self.status()

    def disconnect(self,forcestop=False):
        # wind will call stop() automatically
        if forcestop:
            w.stop()
        print("wind has been stopped")   
        return True

    def get_par_string(self,par_list):
        par_string = par_list[0]
        
        if len(par_list)<2:
            return par_string
        
        for i in range(len(par_list)-1):
            par_string = par_string+","+ par_list[i+1]

        return par_string

    # query history data from wind
    # type: 1=stock, 2=future
    def get_history_data(self,stock_code,fields,start_day,end_day=datetime.today(),show_log=False):    
        if show_log:
            print ("[get_history_data] %s,%s,%s,%s" %(stock_code,fields,start_day,end_day))       
        
        wind_data = w.wsd(stock_code, fields, start_day, end_day, "TradingCalendar=CZCE") #,showblank=0

        if show_log:
            print("[get_history_data] ErrorCode=%d" %wind_data.ErrorCode)
        return wind_data

    def wset(self, view_name,sector_id):
        return w.wset(view_name,sector_id)

    def get_init_day(self,stock_code,type):

        if type==0: #stock
            init_day = w.wss(stock_code,"ipo_date")
        elif type == 1: #etf 
            init_day = w.wss(stock_code,"carrydate")
        elif type == 2: # ab fund
            init_day = w.wss(stock_code,"fund_setupdate")            

        return init_day.Data[0][0]