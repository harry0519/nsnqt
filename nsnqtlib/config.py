from nsnqtlib.servers import serverlist 
import configparser as cp

# config.ini template
#[db]
#user=xxx
#passwd=xxx
config = cp.ConfigParser()
config.read('config.ini')


# print(config.sections())
#Use Aliyun environment settings
DB_SERVER = serverlist.ALIYUN_SERVERS_IP
DB_PORT = serverlist.ALIYUN_MONGODB_PORT
USER = config['db']['user'] #serverlist.ALIYUN_DBUSER_NAME
PWD =  config['db']['passwd']  #serverlist.ALIYUN_DB_PWD
AUTHDBNAME = "admin"

# #Use default local server
# DB_SERVER = serverlist.LOCAL_SERVER_IP
# DB_PORT = serverlist.LOCAL_MONGODB_PORT
# USER = ""
# PWD = ""
# AUTHDBNAME = ""

# #Use Harry's home environment
# DB_SERVER = serverlist.HJ_SERVER_LIST
# DB_PORT = serverlist.HJ_MONGODB_PORT
# USER = ""
# PWD = ""
# AUTHDBNAME = ""

# reployto = 'nsnqt_mail@163.com'
# mail_host = 'smtp.163.com'
# mail_user = 'nsnqt_mail@163.com'
# sender = "nsnqt_mail@163.com"
# mail_pass = 'nokia1234'


reployto = '437270866@qq.com'
mail_host = 'smtp.qq.com'
mail_user = '437270866@qq.com'
sender = "437270866@qq.com"
mail_pass = 'dmilinavphovbjih'

receivers = ["04yylxsxh@163.com","harry202@163.com","wangxian.111@163.com","zhouhua1978@163.com"]
mail_port = 25




