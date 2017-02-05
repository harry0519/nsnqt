# -*- coding: utf-8 -*-
#                前收盘     , 开盘 , 最高  , 最低 ,  收盘 , 成交量  , 成交金额, 成交笔数  ,持仓量, 单位净值
base_fields   = ["pre_close","open","high","low","close","volume","amt"]
stock_fields  =                                                           "dealnum"
future_fields =                                                                      "oi"
fund_fields   =                                                                             "nav"

FIELD_SECURITY_GENERAL = "sec_code", "sec_name","close_price","total_market_value","mkt_cap_float",\
                         "trade_status","last_trade_day","ipo_day","province","sec_type","listing_board","exchange"
FIELD_COMPANY_GENERAL = "company_name","inception_date","ipo_date","outstanding_shares","sec_type",\
                        "regcapital","chairman","discloser","address","office","zipcode", "telephone","fax","website","comp_name_eng"

# 可转债
cbond_list = ["129031.SZ","128013.SZ","128012.SZ","128011.SZ","128010.SZ","128009.SZ","128008.SZ","128007.SZ","128006.SZ",\
             "128005.SZ","128004.SZ","128003.SZ","128002.SZ","128001.SZ","127003.SZ","127002.SZ","127001.SZ","126729.SZ",\
             "125887.SZ","125731.SZ","125089.SZ","123001.SZ","120001.SZ","113501.SH","113010.SH","113009.SH","113008.SH",\
             "113007.SH","113006.SH","113005.SH","113003.SH","113002.SH","113001.SH","110035.SH","110034.SH","110033.SH",\
             "110032.SH","110031.SH","110030.SH","110029.SH","110028.SH","110027.SH","110025.SH","110024.SH","110022.SH",\
             "110020.SH","110019.SH","110018.SH","110017.SH","110016.SH","110015.SH","110013.SH","110012.SH","110011.SH",\
             "110009.SH","110007.SH","110003.SH"]

index_list = ["600900"]
etf_list = ['123456']
"""
判断代码是属于那种类型
:return str 返回code类型, fund 基金 stock 股票
"""
def get_code_type(code):

    assert type(code) is str, 'stock code need str type'

    if code.startswith(('00','01','02','03', '30', '60','61','62','63','stock')):
        return 'stock'
    elif code in cbond_list:
        return 'cbond'
    elif code in index_list:
        return 'index'
    elif code in etf_list:
        return 'etf'
    return 'fund'

def get_quote_string(code):
    quote_string = ",".join(base_fields)
    quote_list = base_fields
    stype = get_code_type(code)

    if stype in ['stock','cbond','index'] :
        quote_string = quote_string + ','+ stock_fields
        quote_list.append(stock_fields)
    elif stype == 'etf' or stype == 'fund':
        quote_string = fund_fields
        quote_list= fund_list
    elif stype == 'future':
        quote_string == quote_string + ','+future_fields
        quote_list.append(future_fields)

    return quote_string, quote_list

 

