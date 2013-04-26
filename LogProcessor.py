import os
import SourceParser
import time

class LogProcess(object):
    """
    UPET(USPTO Patent Exploring Tool)
        provides Python code for downloading, parsing, and loading USPTO patent bulk data into a local MySQL database.
    Website:
        http://abel.lis.illinois.edu/upet/
    Authors:
        Qiyuan Liu (http://liuqiyuan.com, qliu14@illinois.edu),
        Vetle I. Torvik (http://people.lis.illinois.edu/~vtorvik/, vtorvik@illinois.edu)
    Updated:
        12/09/2012
    """
    """
    Used to write log files for all the parsers.
    """
    def __init__(self):
        self.ls=[]
        self.logPath_P=os.getcwd().replace('\\','/')+'/LOG/LOG_P'
        self.logPath_G=os.getcwd().replace('\\','/')+'/LOG/LOG_G'
        self.logPath_PAIR=os.getcwd().replace('\\','/')+'/LOG/LOG_PAIR'
        self.logPath_PAIR_Error=os.getcwd().replace('\\','/')+'/LOG/LOG_PAIR_ERROR'

        self.links_P=[]
        self.links_G=[]
        self.links_PAIR=[]


    # append a new line into the log file
    def write(self,filePath,fileLine):
        #a line shoud be like '[dateTime \t] fileName \t URL \t status'
        f_log=open(filePath,'a')
        dateTime=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        f_log.write(dateTime+'\t'+fileLine+'\n')
        f_log.close()
        #print 'Log info. [{0}] has been appended into the log file at:\n {1}'.format(fileLine,filePath)

    # append a new list into the log file
    def writeList(self,filePath,fileList):
        f_log=open(filePath,'a')
        f_log.writelines(fileList)
        f_log.close()
        print 'Log info. List [{0}] has been appended into the log file at:\n {1}'.format(fileList,filePath)

