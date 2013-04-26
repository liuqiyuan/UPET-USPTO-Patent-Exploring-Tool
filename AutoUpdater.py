import LogProcessor
import SourceParser
import os
import GrantsParser
import PublicationsParser
import PAIRParserSeg

class AutoUpdate(object):
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
    Used for automatic updating in a specific period of time.(Weekly)
    1.check log file to obtain processed files list
    2.check web to obtain all processable files list
    3.get unprocessed files list and ask user to continue or exit

    Note that this updater only checks the new data in the format of XML4
    And the PAIR dataset (which needs to be processed separately) has been omitted
    """
    def __init__(self):
        self.logPath_P=os.getcwd().replace('\\','/')+'/LOG/LOG_P'
        self.logPath_G=os.getcwd().replace('\\','/')+'/LOG/LOG_G'
        self.logPath_PAIR=os.getcwd().replace('\\','/')+'/LOG/LOG_PAIR'
        self.urlLinkName_PAIR='http://commondatastorage.googleapis.com/uspto-pair/applications/[replaceNum].zip'

        self.allG=[]
        self.allG_XML4=[]
        self.allP=[]
        self.allPAIR=[]

        self.processedG=[]
        self.processedP=[]
        self.processedPAIR=[]

        self.sprocessedG=[]
        self.sprocessedP=[]
        self.sprocessedPAIR=[]
        
        self.unprocessedG=[]
        self.unprocessedP=[]
        self.unprocessedPAIR=[]

    def checkAll(self):
        log=LogProcessor.LogProcess()
        f_log_g=open(self.logPath_G,'rb')
        f_log_p=open(self.logPath_P,'rb')
        f_log_pair=open(self.logPath_PAIR,'rb')
        self.processedG=f_log_g.readlines()
        self.processedP=f_log_p.readlines()
        #self.processedPAIR=f_log_pair.readlines()
        for i in self.processedG:
            if(i.split('\t')[4].strip()=='Processed' or i.split('\t')[4].strip()=='Passed'):
                fileName=i.split('\t')[1]
                if(fileName not in self.sprocessedG):
                    self.sprocessedG.append(fileName)
        for i in self.processedP:
            if(i.split('\t')[4].strip()=='Processed'):
                fileName=i.split('\t')[1]
                if(fileName not in self.sprocessedP):
                    self.sprocessedP.append(fileName)
##        for i in self.processedPAIR:
##            if(i.split('\t')[4].strip()=='Processed'):
##                fileName=i.split('\t')[2]
##                if(fileName not in self.sprocessedPAIR):
##                    self.sprocessedPAIR.append(fileName)
        sp=SourceParser.SourceParser()
        self.allG=sp.getdLinksPG()
        self.allP=sp.getdLinksPP()
        #self.allPAIR=sp.getdLinksPAIR()
        
        self.allG_XML4=sp.getFileNamesPG_XML4()
        self.allP_XML4=sp.getFileNamesPP_XML4()
        
        self.unprocessedG=list(set(self.allG_XML4)-set(self.sprocessedG))
        self.unprocessedP=list(set(self.allP_XML4)-set(self.sprocessedP))
        #self.unprocessedPAIR=list(set(self.allPAIR)-set(self.sprocessedPAIR))

if __name__=="__main__":
    print '*'*21
    print 'Check for updates now...'
    print '*'*21
    auto=AutoUpdate()
    auto.checkAll()
    print '='*21+' Data Statistics '+'='*21
    print '          \tGRA \tPUB \tPAIR'
    print 'CurrentAll    \t'+str(len(auto.allG))+'\t'+str(len(auto.allP))+'\t'+str(len(auto.allPAIR))
    print 'Processed     \t'+str(len(auto.processedG))+'\t'+str(len(auto.processedP))+'\t'+str(len(auto.processedPAIR))
    print 'SProcessed    \t'+str(len(auto.sprocessedG))+'\t'+str(len(auto.sprocessedP))+'\t'+str(len(auto.sprocessedPAIR))
    print 'SprocessedXML4\t'+str(len(auto.allG_XML4))+'\t'+str(len(auto.allP_XML4))
    print 'UnProcessed   \t'+str(len(auto.unprocessedG))+'\t'+str(len(auto.unprocessedP))+'\t'+str(len(auto.unprocessedPAIR))
    print '='*21+' Grants Updates '+'='*21
    if(len(auto.unprocessedG)>0):
        text=raw_input('Grants:{0} files to be updated!\nPress \'Y/y\' to continue.'.format(len(auto.unprocessedG)))
        if(text.upper()=='Y'):
            GrantsParser.update(auto.unprocessedG)
        else:
            pass
    print '='*21+' Publications Updates '+'='*21
    if(len(auto.unprocessedP)>0):
        text=raw_input('Publciatoins:{0} files to be updated!\nPress \'Y/y\' to continue.'.format(len(auto.unprocessedP)))
        if(text.upper()=='Y'):
            PublicationsParser.update(auto.unprocessedP)
        else:
            pass
    print '='*21+' PAIR Data Updates '+'='*21
    if(len(auto.unprocessedPAIR)>0):
        text=raw_input('PAIR Data:{0} files to be updated!\nPress \'Y/y\' to continue.'.format(len(auto.unprocessedPAIR)))
        if(text.upper()=='Y'):
            PAIRParserSeg.multiProcess(auto.unprocessedPAIR,1000)
        else:
            pass
    raw_input('All updates have been processed successfully!')


