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
db.stock.insert_one({"number":"600000","price":111})       #往test数据库下的stock表（collection）插入一条记录

#####################################################################################################
print(db.stock.find_one({"number":"600000"}))  #获取test数据库中stock表里的一条记录number=600000的记录，并打印到屏幕
#输出：{'number': '600000', '_id': ObjectId('57d81238181a1f21b8a5e490')}

######################################################################################################
db.stock.update_one({"number":"600000"},{"$set":{"name":"大盘指数"}}) #更新一条number为600000的记录，加入name值为大盘指数
                                                                      #如果字段不存在，则直接增加，如果存在则更新值
#用find命令看到的输出值{'number': '600000', 'name': '大盘指数', '_id': ObjectId('57d81238181a1f21b8a5e490')}                                                                      
# db.stock.update_one({"number":"600000"},{"name":"大盘指数"})  这条命令会把一条记录为number为600000的直接替换为name=大盘指数
#####################################################################################################
for  i in db.stock.find({"number":"600000"}):  #获取所有test数据库中tock表里number=600000的记录，并打印到屏幕
    print(i)
    


