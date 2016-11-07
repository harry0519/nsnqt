# -*- coding:utf-8 -*-
import random
class StockIndicator(object):
    '''
    various kinds of stock indicator method
    '''
    def __init__(self,):
        pass
    
    def islowestvolume(self,data,section=60):
        if (len(data) >= section) and (data[0] == min(data[0:section])):
            return True
        return False
    
    def getaverageprice(self,data,):
        pass
    
    def getnewindex(self,datas,newdata,l,base=0):
        '''datas:should be sorted from min to max,
           newdats: the data need to check the position in the sorted datas
           l:len of data
           base:first position of the datas in origin datas
        '''
        index = int(l/2)
        if datas[index] > newdata:
            if l==1:return base
            d = datas[:index]
            nl = index
            return self.getnewindex(d,newdata,nl,base)
        elif datas[index] < newdata:
            if l<=2:return base+l
            d = datas[index+1:] 
            nl = int((l-1)/2)
            return self.getnewindex(d,newdata,nl,base+index+1)
        elif datas[index] == newdata:
            return base+index
    
if __name__ == '__main__':
    s= StockIndicator()
    data=random.sample(range(100),100)
    print(data)
    datas=sorted(data[:10])
    print (datas)
    for i in data:
        print (s.getnewindex(datas,i,10))
    
    
    
    
    