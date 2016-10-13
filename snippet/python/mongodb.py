def connect_to_mdb(ip="localhost", port=27017):
    server_ip = ip
    server_port = port
    db_client = MongoClient(server_ip, server_port)
    
    return db_client