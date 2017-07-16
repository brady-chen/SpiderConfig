# -*- coding:utf-8 -*-
# version: 1.5

import logging, requests, getpass, sys, time, traceback


#定义MyLog类
class MyLog(object):
    '''
    这个类用于创建一个自用的log
    '''
    def __init__(self): #类的构造函数
        pass


    '''日志初始化'''
    def init(self, logFile):
        """
        封装为函数是为了先获取log文件名后再进行初始化
        :param logFile: 在调用的地方输入log文件名
        :return: 日志初始化
        """
        user = getpass.getuser()
        self.logger = logging.getLogger(user)
        self.logger.setLevel(logging.DEBUG)
        #self.logFile = sys.argv[0][0:-3] + '.log' #日记文件名
        formatter = logging.Formatter('%(asctime)-12s %(levelname)-8s %(name)-10s %(message)-12s')

        '''日志显示到屏幕上并输出到日志文件内'''
        logHand = logging.FileHandler(logFile)
        logHand.setFormatter(formatter)
        logHand.setLevel(logging.DEBUG) #所有信息都会被记录到logfile中

        logHandSt = logging.StreamHandler()
        logHandSt.setFormatter(formatter)

        self.logger.addHandler(logHand)
        self.logger.addHandler(logHandSt)


    '''日志的五个级别对应以下的5个函数'''
    def debug(self, msg):
        """
        详细的信息,通常只出现在诊断问题上
        :param msg: log信息
        :return: 记录log信息
        """
        self.logger.debug(msg)

    def info(self, msg):
        """
        确认一切按预期运行
        :param msg:log信息
        :return:记录log信息
        """
        self.logger.info(msg)

    def warn(self, msg):
        """
        一个迹象表明,一些意想不到的事情发生了,或表明一些问题在不久的将来(例如。磁盘空间低”)。这个软件还能按预期工作。
        :param msg:log信息
        :return:记录log信息
        """
        self.logger.warn(msg)

    def error(self, msg):
        """
        更严重的问题,软件没能执行一些功能
        :param msg:log信息
        :return:记录log信息
        """
        self.logger.error(msg)

    def critical(self, msg):
        """
        一个严重的错误,这表明程序本身可能无法继续运行
        :param msg:log信息
        :return:记录log信息
        """
        self.logger.critical(msg)

    def fun_log_type(self, num, msg):
        """
        :param num: 日志级别数字 
        :param msg: 日志消息
        :return: 
        """
        if num == 1:
            return self.debug(msg)
        elif num == 2 :
            return self.debug(msg)
        elif num == 3:
            return self.debug(msg)
        elif num == 4:
            return self.debug(msg)
        elif num == 5:
            return self.debug(msg)

    def deco_log(self, log_name, fun_name, check_error=False):
        """
        :param fun_name: 输入正在运行的函数的名字
        :param log_name: 定义日志文件的名字，默认为空,建议输入sys.argv[0][0:-3] + '.log'，使用本py文件命名log
        :param check_error: 是否启用此装饰器，输入True或False，默认为False
        :return:报错或显示“运行正常”并计时
        """
        # 每个py文件命名不同所以需要每次都初始化重命名一次
        self.init(log_name)
        # 因为python2没有nonlocal，所以用列表来代替非局部变量
        status = [1]
        msg = [1]
        if check_error:
            def log(func):
                def record(*args, **kwargs):
                    try:
                        t0 = time.time()
                        back = func(*args, **kwargs)
                        #计时
                        run_time = time.time() - t0
                        #如果函数没报错，则输出info信息并显示运行正常
                        status[0] = 2
                        msg[0] = "%s函数运行正常，耗时%s秒" %(fun_name, run_time)
                        return back
                    # sys._getframe().f_code.co_name可以获取当前函数名
                    except IndexError, e:
                        status[0] = 3
                        msg[0] = "出错于:%s函数，遍历错误\n原因为:%s\n详细信息为:\n%s" % (fun_name, e, traceback.format_exc())
                    except requests.ConnectionError, e:
                        status[0] = 4
                        msg[0] = "出错于:%s函数，网络问题异常，如DNS查询失败、拒绝连接等\n原因为:%s\n详细信息为:\n%s" % (fun_name, e, traceback.format_exc())
                    except requests.TooManyRedirects, e:
                        status[0] = 4
                        msg[0] = "出错于:%s函数，超过了设定的最大重定向次数\n原因为:%s\n详细信息为:\n%s" % (fun_name, e, traceback.format_exc())
                    except requests.HTTPError, e:
                        status[0] = 4
                        msg[0] = "出错于:%s函数，非200成功状态码\n原因为:%s\n详细信息为:\n%s" % (fun_name, e, traceback.format_exc())
                    except requests.RequestException, e:
                        status[0] = 4
                        msg[0] = "出错于:%s函数，requests的父异常\n原因为:%s\n详细信息为:\n%s" % (fun_name, e, traceback.format_exc())
                    except Exception, e:
                        status[0] = 5
                        msg[0] = "出错于:%s函数，未命名错误\n原因为:%s\n详细信息为:\n%s" % (fun_name, e, traceback.format_exc())
                    finally:
                        self.fun_log_type(status[0], msg[0])
                return record
        else:
            def log(func):
                return func
        return log
