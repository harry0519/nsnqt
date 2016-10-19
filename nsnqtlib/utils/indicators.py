# -*- coding:utf-8 -*-

class StockIndicator(object):
    '''
    various kinds of stock indicator method
    '''
    def __init__(self,):
        pass
    
    def islowestvolume(self,data,section=60):
        if len(data) >= section and data[0] == min(data[0:section]):
            return True
        return False
    
    def getaverageprice(self,data,):
        