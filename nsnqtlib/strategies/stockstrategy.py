# -*- coding:utf-8 -*-
from  nsnqtlib.db.mongodb import MongoDB
import threading
import time
import datetime
DATES = []
HOLDS=[]
RESULTS=[]

class strategy1(object):
    '''
    trading volume is the lowest in 60 days
    '''
    def __init__(self,stock="600455.SH"):
        self.m = MongoDB()
    
    def _getdata(self,db="ml_security_table",collection="600455.SH"):   
        query = self.m.read_data(db,collection,filt={"date":{"$gt": datetime.datetime(2013, 1, 1, 0, 0, 0,0)}})
        return self.m.format2dataframe(query)
    
    def histofyreturn(self,db="ml_security_table",table=""):
        holding = []
        w=40
#         stocklist = self.m.getallcollections(db)
        df = self._getdata(collection=table)
#         df.to_csv('600455.csv')
        count=1
        origindata=[]
        lst = [l for l in df[["date","volume","close","high"]].fillna(0).values if l[1] !=0]
        for line in lst:
            if line[1] == 0:continue
            origindata.append(line[1])
            if count == w:
                sorteddata=sorted(origindata)
            elif count >w:
                index = self.getnewindex(sorteddata,line[1],w)
                for h in holding:
                    if (line[3]-h[1])/h[1]>=0.1:
#                         print (count-h[0])
                        print (0.1)
                        RESULTS.append(0.1)
                        holding.remove(h)
                        HOLDS.append(count-h[0])
                    elif (line[3]-h[1])/h[1]<=-0.10 or count-h[0] > 20:
                        if count-h[0] > 20:
                            print ("{},{}".format((line[3]-h[1])/h[1],line[0]))
                        else:
                            print ("{},{}".format(-0.1,line[0]))
                        RESULTS.append((line[3]-h[1])/h[1])
                        HOLDS.append(count-h[0])
                        holding.remove(h)
                if index ==0:
                    holding.append((count,line[2],line[0]))
                    DATES.append(line[0])
#                     print ("{} {} {}".format(line[0],index,(lst[count+2][2]-lst[count][2])/lst[count][2]))
                sorteddata.insert(index,line[1])
                sorteddata.remove(origindata[0])
                del origindata[0]
            count +=1
        print (table)
#         print (holding)
            
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
    
        
            
# threads = []
# t1 = threading.Thread(target=music,args=(u'爱情买卖',))
# threads.append(t1)
# t2 = threading.Thread(target=move,args=(u'阿凡达',))
# threads.append(t2)

# if __name__ == '__main__':
#     for t in threads:
#         t.setDaemon(True)
#         t.start()    

# def single(table,s):
# #     s=strategy1()
#     s.histofyreturn(table=table)
# 
# def thread_store_all_stock(lst,s):
#     count=0
#     for i in lst:
#         count+=1
#         while  len(threading.enumerate())>=40:
#             time.sleep(1)
# #             print (len(threading.enumerate()))
#         print (count)
#         t = threading.Thread(target=single,args=(i,s))
#         t.setDaemon(True)
#         t.start()
#     t.join()
      
s=strategy1()
stocklist = s.m.getallcollections("ml_security_table")
# thread_store_all_stock(stocklist,s) 还没有单线程效率高

for i in stocklist:
#     print (i)  
    s.histofyreturn(table=i)

print (len(set(DATES)))
print (sum(HOLDS)/len(HOLDS))





