# -*- coding:utf-8 -*- 
import smtplib
from email.mime.text import MIMEText
from email.header import Header
mail_host = 'smtp.163.com'
mail_user = 'nsnqt_mail@163.com'
mail_pass = 'nokia1234'
sender = "nsnqt_mail@163.com"
receivers = ["04yylxsxh@163.com",]


message = MIMEText('<html><h1>你到底要怎样才不算是垃圾邮件</h1></html>','html','utf-8')
# message['From'] = Header("nsnqt_mail@163.com",'utf-8')
message['From'] = mail_user
# message['To'] = Header("04yylxsxh@163.com",'utf-8')
message['To'] = "04yylxsxh@163.com"
subject = '我就是 '
message['Subject'] = subject

smtp = smtplib.SMTP()
smtp.connect(mail_host,25)
smtp.login(mail_user,mail_pass)
smtp.sendmail(sender,receivers,message.as_string())
smtp.quit() 


