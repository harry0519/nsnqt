# -*- coding:utf-8 -*- 
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from nsnqtlib import config

class mail():
    def __init__(self,mail_host=config.mail_host,
                      mail_port=config.mail_port,
                      mail_user=config.mail_user,
                      mail_pass=config.mail_pass,
                      sender=config.sender,
                      reployto=config.reployto,
                      receivers=config.receivers):
        
        self.reployto = reployto
        self.mail_host = mail_host
        self.mail_port = mail_port
        self.mail_user = mail_user
        self.mail_pass = mail_pass
        self.receivers = receivers
        self.sender = sender
        
        self.smtp = self.connect()
        self.message = MIMEText("")
        
    def connect(self):
        smtp = smtplib.SMTP()
        smtp.connect(self.mail_host,self.mail_port)
        smtp.login(self.mail_user,self.mail_pass)
        return smtp
    
    def setmessage(self,subject="None",content="None",subtype="plain",):
        message = MIMEText(content,subtype,'utf-8')
        message['From'] = self.mail_user
        message['To'] = ",".join(self.receivers)
        message['Subject'] = subject 
        self.message = message.as_string() 
    
    def disconnect(self):
        self.smtp.quit()
    
    def sendmail(self):
        sender = self.sender
        receivers = self.receivers
        message = self.message
        self.smtp.sendmail(sender,receivers,message)

# if __name__ == '__main__':
#     m = mail()
#     m.setmessage("我就是测试下", "test for send mail in python")
#     m.sendmail()
#     m.disconnect()