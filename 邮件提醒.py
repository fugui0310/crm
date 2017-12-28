import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr


# class Email(object):
#     def __init__(self):
#         self.email = "fg0310@126.com"
#         self.user = "fugui"
#         self.pwd = 'yfg898228'
#
#     def send(self, subject, body, to, name):
msg = MIMEText('ccccccccc', 'plain', 'utf-8')  # 发送内容
msg['From'] = formataddr(["fugui", "542770353@qq.com"])  # 发件人
msg['To'] = formataddr(['liangduanqi', '1125191117@qq.com'])  # 收件人
msg['Subject'] = 'xxxx'  # 主题

server = smtplib.SMTP('smtp.qq.com', 25) # SMTP服务
server.login('542770353@qq.com', 'yedneiqrvgptbcbc'), # 邮箱用户名和密码
server.sendmail('542770353@qq.com', '1125191117@qq.com', msg.as_string())  # 发送者和接收者
server.quit()

#
# foo = Email()
# foo.send('收到？', 'qwqeqeqeqeq', '1125191117@qq.com', 'liangduanqi')
