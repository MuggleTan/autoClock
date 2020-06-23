from selenium import webdriver
import time
import datetime 
from email.mime.text import MIMEText
from email.header import Header
from smtplib import SMTP_SSL
import sys

driver = webdriver.Chrome(executable_path=r'./chromedriver.exe')

# 计算用户个数
def countUser():
    num = 0
    for line in allUser: 
        num += 1
    return num

# 从文件中读取用户
def readUser():
    num = 0
    for line in allUser:
        line = line.strip().split(" ")   
        for i in range(4):
            try:
                userList[num][i] = line[i]
            except:
                userList[num][i] = ''
        num += 1
# 登录打卡网页
def login(user):
    global loginfo
    # 打开打卡网页
    driver.get('https://xgzx.hunau.edu.cn/yiban/login')
    # 等浏览器与Selenium完美契合之后再进行下一步动作
    driver.implicitly_wait(2)
    # 输入用户名和密码
    log.write(user[0] + " 开始登陆\n")
    loginfo += user[0] + " 开始登陆\n"
    print(user[0] + " 开始登陆")
    driver.find_element_by_name("username").send_keys(user[1])  # user_pwd
    driver.find_element_by_name("password").send_keys(user[2])  # user_pwd
    time.sleep(2)
    # 点击登录按钮 
    driver.find_element_by_xpath('//*[@id="app"]/div/div[4]/div/button').click()
    time.sleep(2)
    title = driver.title
    # 根据网页的title判断是否登陆成功
    if title == '疫情防控打卡-QZBPS 平台-湖南农业大学':
        log.write(user[0] + " 登陆成功\n")
        print(user[0] + " 登录成功\n")
        loginfo += user[0] + " 登录成功\n"
    else:
        log.write(user[0] + " 登录异常\n")
        loginfo += user[0] + " 登录异常\n"
        raise Exception("登录异常")
    time.sleep(2)

# 打卡
def clock(user):
    global loginfo
    loginfo += user[0] + " 开始打卡\n"
    log.write(user[0] + " 开始打卡\n")
    print(user[0] + " 开始打卡")
    # 点击每日打卡栏目
    driver.find_element_by_xpath('//*[@id="app"]/div/div/div[1]/div/div[2]/span').click()
    time.sleep(2)
    # 获取按钮中的文字，用来判断判断是否已打卡
    status = driver.find_element_by_xpath('//*[@id="app"]/div/div/div[2]/div[1]/button/span').text

    if status == '今日已提交':
        print('今日已打卡')
        log.write(user[0] + " 今日已提交\n\n")
        loginfo += user[0] + " 今日已提交\n\n"
    else:
        # 打钩确认
        driver.find_element_by_xpath('//*[@id="app"]/div/div/div[2]/div[1]/div[24]/div/div').click()
        time.sleep(2)
        # 提交按钮
        driver.find_element_by_xpath('//*[@id="app"]/div/div/div[2]/div[1]/button').click()
        time.sleep(2)
        status = driver.find_element_by_xpath('//*[@id="app"]/div/div/div[2]/div[1]/button/span').text
        if status == '今日已提交':
            if user[3] != '':
                sendEmail(user,'打卡成功','  已于' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                            + ' 帮您成功打卡！')
                log.write(user[0] + ' 邮件已发送')
                loginfo += user[0] + ' 邮件已发送'
                print(user[0] + " 打卡成功\n")
                log.write(user[0] + '打卡成功\n\n')
                loginfo += user[0] + '打卡成功\n\n'
        else:
            print(user[0] + " 打卡异常\n")
            log.write(user[0] + '打卡异常\n')
            loginfo += user[0] + '打卡异常\n'
            raise Exception("打卡异常")
        time.sleep(2)

# 登录邮件服务器 返回一个smtp对象
def emailLogin():
    global loginfo
    #qq邮箱smtp服务器
    host_server = 'smtp.qq.com'
    #sender_qq为发件人的qq号码
    sender_qq = '1454977287'
    #pwd为qq邮箱的授权码 
    pwd = '' 
    
    try:
        #ssl登录
        smtp = SMTP_SSL(host_server)
        #set_debuglevel()是用来调试的。参数值为1表示开启调试模式，参数值为0关闭调试模式
        smtp.set_debuglevel(0)
        smtp.ehlo(host_server)
        smtp.login(sender_qq, pwd)
    except:
        log.write("邮件服务器登陆失败\n" + repr(sys.exc_info()[1]) + '\n')
        loginfo += "邮件服务器登陆失败\n" + repr(sys.exc_info()[1]) + '\n'
    return smtp

# 发送邮件
def sendEmail(user,title,content):
    global loginfo
    #发件人的邮箱
    sender_qq_mail = 'tan.xuyang@qq.com'
    #收件人邮箱
    receiver = user[3]
    
    #邮件标题
    mail_title = title
    try:
        #邮件的正文内容
        mail_content = '尊敬的用户 ' + user[0] + '您好：\n' + content
        msg = MIMEText(mail_content, "plain", 'utf-8')
        msg["Subject"] = Header(mail_title, 'utf-8')
        msg["From"] = sender_qq_mail
        msg["To"] = receiver
        smtp.sendmail(sender_qq_mail, receiver, msg.as_string())
    except:
        log.write("邮件发送异常\n" + repr(sys.exc_info()[1]) + '\n')
        loginfo += "邮件发送异常\n" + repr(sys.exc_info()[1]) + '\n'

# 异常处理
def exceptionHandle(user,msg):
    global loginfo
    log.write(user[0] + repr(sys.exc_info()[1]) + '\n\n')
    print(user[0] + repr(sys.exc_info()[1]) + '\n\n')
    if user[3] != '':
        sendEmail(user,msg + '，请联系管理员','打卡发生异常，请联系管理员\n错误类型：' + repr(sys.exc_info()[1]))
    else:
        sendEmail(userList[0],user[0] + msg,repr(sys.exc_info()[1]))


if __name__ == "__main__":
    loginfo = '打卡日志：\n'
    # 打开日志文件
    log = open('./log.txt','a',encoding='utf-8')
    log.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\n')
    loginfo += datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\n'
    # 读取用户数据
    userf = open("./user.txt",mode="r",encoding='utf-8')
    allUser = userf.readlines()
    userf.close()

    # 将用户数据转换为列表格式
    userList = [[0 for i in range(4)] for j in range(countUser())]
    readUser()
    # print(userList)

    # 登录邮件服务器
    smtp = emailLogin()
    
    # 打卡签到
    for user in userList:
        try:
            login(user)
            try:
                clock(user)
            except:
                exceptionHandle(user,'打卡异常')
        except:
            exceptionHandle(user,'登录异常')

    sendEmail(userList[0],'打卡日志',loginfo)
    smtp.quit()
    driver.quit()
    log.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\n\n')
    log.close()