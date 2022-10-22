import smtplib
from email.mime.text import MIMEText
from email.header import Header
def send_email_to_remind():
    
    # 第三方 SMTP 服务
    mail_host="smtp.163.com"  #设置服务器
    mail_user="hello_huhao"    #用户名
    mail_pass="MWJBLDKZTBINZPHR"   #口令 
    sender = 'hello_huhao@163.com'
    receivers = ['980850497@qq.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
    
    message = MIMEText('hello! Your program has been interrupted, please quickly find the cause and RUN!!!!', 'plain', 'utf-8')
    message['From'] = Header("The server used by Hao Hu")
    message['To'] =  Header("Hao Hu")
    
    subject = 'vision_reptile 程序中断提醒'
    message['Subject'] = Header(subject, 'utf-8')
    
    
    try:
        smtpObj = smtplib.SMTP() 
        smtpObj.connect(mail_host, 25)    # 25 为 SMTP 端口号
        smtpObj.login(mail_user,mail_pass)  
        smtpObj.sendmail(sender, receivers, message.as_string())
        print("已经发送邮件提醒程序中断")
    except smtplib.SMTPException:
        print("Error: 无法发送邮件")

