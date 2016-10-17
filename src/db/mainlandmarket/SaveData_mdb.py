
from pymongo import MongoClient

def connect_to_mdb(ip="localhost", port=27017):
    client = MongoClient(ip, port)
    print("connected")
    return client
    
def disconnect_to_mdb():
    print("disconnected")
        
def save_data_to_mdb(data_set):
    print("Start to save data to mongodb")
    connect_to_mdb()
    # save data here
    # ...
    
    disconnect_to_mdb()
    print("data have been saved to mongodb")
    
def get_data_from_mdb(sql):
    print(sql)