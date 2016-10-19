

class BaseDB(object):
    __server_ip = "127.0.0.1"
    __server_port = 27017
    __user_name = ""
    __pwd = ""
    _db_session = None

    def __init__(self, ip="127.0.0.1", port=27017, user_name="", pwd="",authdb="admin"):
        self.__server_ip = ip
        self.__server_port = port
        self.__user_name = user_name
        self.__pwd = pwd
        self.__authdb = authdb 

    def connect(self):
        pass

    def disconnect(self):
        pass

    def save_data(self, db_name, table_name, dataset, fields):
        pass

    def read_data(self, db_name, table_name, fields):
        pass

    def test(self):
        print("hello from basedb")