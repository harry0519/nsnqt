# -*- coding:utf-8 -*- 
'''
Created on 2016��9��11��
@author: 04yyl
'''

from pymongo import MongoClient

client = MongoClient("localhost", 27017)       #链接数据库服务器
client.test.authenticate("xuhshen1","xuhshen")  #test数据库用户名和密码验证
db = client.test                               #获取test数据库连接

#####################################################################################################
db.stock.insert_one({"number":"600000"})       #往test数据库下的stock表（collection）插入一条记录

#####################################################################################################
print(db.stock.find_one({"number":"600000"}))  #获取test数据库中stock表里的一条记录number=600000的记录
#输出：{'number': '600000', '_id': ObjectId('57d81238181a1f21b8a5e490')}


#####################################################################################################
for  i in db.stock.find({"number":"600000"}):  #获取所有test数据库中tock表里number=600000的记录
    print(i)