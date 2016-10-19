from pymongo import MongoClient

class BaseDB:
    __server_ip = "127.0.0.1"
    __server_port = 27017
    __user_name = ""
    __pwd = ""
    __db_session = None

    def __init__(self, ip="127.0.0.1", port=27017, user_name="", pwd="",authdb="admin"):
        self.__server_ip = ip
        self.__server_port = port
        self.__user_name = user_name
        self.__pwd = pwd
        self.__authdb = authdb 

    def connect(self):
        self.__db_session = MongoClient(self.__server_ip, self.__server_port)
        if  self.__user_name:  
            eval("self.__db_session.{}".format(self.__authdb)).authenticate(self.__user_name,self.__pwd)      
        
        print("connected to "+self.__server_ip)
        return self.__db_session

    def disconnect(self):
        return self.__db_session.close()

    def save_data(seflf, db_name, table_name, dataset, fields):
        pass

    def read_data(seflf, db_name, table_name, fields):
        pass

    def test(self):
        print("hello from base.MongoDB")