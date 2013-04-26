import urllib
from HTMLParser import HTMLParser
import re
import os
import time
import zipfile
import LogProcessor

class SourceParser:
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
    Used to access the webpage and extract all the downloadable URLs to download Google Patent .zip files AND extract the XML file.
    1. get all the downloadable links of patents
    2. get preprocessed contents of .zip files
    3. return contents to data parsers
    """
    def __init__(self):
        # Patent Grants Variables
        self.urlSource_PG_BD='http://www.google.com/googlebooks/uspto-patents-grants-biblio.html'
        self.urlPattern_PG_BD='(http://storage.googleapis.com/patents/grantbib).*(\.zip)'
        # http://storage.googleapis.com/patents/grantbib/2012/ipgb20120110_wk02.zip
        self.urlPattern_PG_BD_XML4='(http://storage.googleapis.com/patents/grantbib/)[0-9]{4}/ipgb.*(\.zip)'
        self.dLinks_PG_BD=[] # downloadable links (.zip files address)
        self.dLinks_PG_BD_XML4=[] # XML4 data download links
        self.fileDir_PG_BD=os.getcwd().replace('\\','/')+"/ZIP_G"  #'d:/PatentsData/PG_BD'
        self.fileDirG_xml4=os.getcwd().replace('\\','/')+"/ZIP_G/XML4/"  #'d:/PatentsData/PG_BD'
        self.fileDirG_xml2=os.getcwd().replace('\\','/')+"/ZIP_G/XML2/"  #'d:/PatentsData/PG_BD'
        self.fileDirG_xml24=os.getcwd().replace('\\','/')+"/ZIP_G/XML24/"  #'d:/PatentsData/PG_BD'
        self.fileDirG_aps=os.getcwd().replace('\\','/')+"/ZIP_G/APS/"  #'d:/PatentsData/PG_BD'
        self.links_G_XML4=[]
        self.links_G_XML2=[]
        self.links_G_XML2_4=[]
        self.links_G_APS=[]
        #file paths list
        self.files_G_XML4=[]
        self.files_G_XML2=[]
        self.files_G_XML24=[]
        self.files_G_APS=[]
        #file names list
        self.fileNames_G_XML4=[]

        # Patent Application Publications Variables
        self.urlSource_PP_BD='http://www.google.com/googlebooks/uspto-patents-applications-biblio.html'
        self.urlPattern_PP_BD='(http://storage.googleapis.com/patents/appl_bib).*(\.zip)'
        # http://storage.googleapis.com/patents/appl_bib/2012/ipab20120126_wk04.zip
        self.urlPattern_PP_BD_XML4='(http://storage.googleapis.com/patents/appl_bib/)[0-9]{4}/ipab.*(\.zip)'
        self.dLinks_PP_BD=[] # downloadable links (.zip files address)
        self.fileDir_PP_BD=os.getcwd().replace('\\','/')+"/ZIP_P"  #'d:/PatentsData/PA_BD'
        self.fileDirP_xml4=os.getcwd().replace('\\','/')+"/ZIP_P/XML4/"  #'d:/PatentsData/PA_BD'
        self.fileDirP_xml1=os.getcwd().replace('\\','/')+"/ZIP_P/XML1/"  #'d:/PatentsData/PA_BD'
        self.links_P_XML4=[]
        self.links_P_XML1=[]
        self.files_P_XML4=[]
        self.files_P_XML1=[]

        self.fileNames_P_XML4=[]

        # Patent Application Information Retrieval
        self.urlLinkName_PAIR='http://commondatastorage.googleapis.com/uspto-pair/applications/[replaceNum].zip'
        self.urlSource_PAIR=os.getcwd().replace('\\','/')+"/ID/PAIRLinks"
        self.fileDir_PAIR=os.getcwd().replace('\\','/')+'/PAIR'
        self.dLinks_PAIR=[]

        self.fileNames_PARI=[]

        # Public Variables
        self.fileName=''
        self.fileDir=''
        self.filePath=''
        self.filePathXML=''
        self.xmlStr=''
        self.links=[] # links in the Webpage

    def getWebContent(self,url='http://www.google.com'):
        return urllib.urlopen(url).read()

    def matchDownload(self,urlPattern='.*(\.zip)',link=''):
        result=re.match(urlPattern,link)
        try:
            return result.string
        except: #return NoneType
            return None

    def returnMatch(self,pattern,string):
        c=re.compile(pattern)
        m=c.match(string)
        return m

    def returnRegLine(self,line):
        """
        USED FOR REPLACE ERROR CODE FOR HTML 
        HTML escape characters
        """
        c=re.compile('&[a-z|A-Z|0-9]*;')
        ls=c.findall(line)
        for l in ls:
            if(l=='&amp;'):line=line.replace(l,'&#x26;') #'&#38;')
            elif(l=='&lt;'):line=line.replace(l,'&#x3C;') #'&#60;')
            elif(l=='&gt;'):line=line.replace(l,'&#x3E;') #&#62;')
            elif(l=='&quot;'):line=line.replace(l,'&#x22;') #&#34;')
            elif(l=='&lsquo;'):line=line.replace(l,'&#x2018;') #&#8216;')
            elif(l=='&rsquo;'):line=line.replace(l,'&#x2019;') #&#8217;')
            elif(l=='&ldquo;'):line=line.replace(l,'&#x201C;') #&#8220;')
            elif(l=='&rdquo;'):line=line.replace(l,'&#x201D;') #&#8221;')
            elif(l=='&sbquo;'):line=line.replace(l,'&#x201A;') #&#8218;')
            elif(l=='&bdquo;'):line=line.replace(l,'&#x201E;') #&#8222;')
            elif(l=='&ndash;'):line=line.replace(l,'&#x2013;') #&#8211;')
            elif(l=='&mdash;'):line=line.replace(l,'&#x2014;') #&#8212;')
            #elif(l=='&minus;'):line=line.replace(l,'&#8722;')
            #elif(l=='&times;'):line=line.replace(l,'&#215;')
            #elif(l=='&divide;'):line=line.replace(l,'&#247;')
            #elif(l=='&copy;'):line=line.replace(l,'&#169;')
            elif(l=='&lsaquo;'):line=line.replace(l,'&#x2039;')
            elif(l=='&rsaquo;'):line=line.replace(l,'&#x203A;')
            else:
                line=re.sub('&[a-z|A-Z|0-9]*;','|',line)
        return line

    def getdLinksPG(self):
        """
        Used to get all downloadable links of Patent Grants
        """
        content=self.getWebContent(self.urlSource_PG_BD)
        htmlP=LinksParser()
        self.links=htmlP.read(content)
        for i in self.links:
            if(self.matchDownload(self.urlPattern_PG_BD,i)!=None):
                self.dLinks_PG_BD.append(i)
        print '[get patent grants downloadable links successfully! Num:{0}]'.format(len(self.dLinks_PG_BD))
        return self.dLinks_PG_BD

    # get the downloadable links of patent grants
    def getdLinksPG_XML4(self):
        """
        Used to get all downloadable links of Patent Grants with XML4 format
        used to update
        """
        content=self.getWebContent(self.urlSource_PG_BD)
        htmlP=LinksParser()
        self.links=htmlP.read(content)
        for i in self.links:
            if(self.matchDownload(self.urlPattern_PG_BD_XML4,i)!=None):
                self.dLinks_PG_BD_XML4.append(i)
        print '[get patent grants downloadable links successfully! Num:{0}]'.format(len(self.dLinks_PG_BD_XML4))
        return self.dLinks_PG_BD_XML4

    #get the files names of the patent grants
    def getFileNamesPG_XML4(self):
        """
        Used to get all file names of patent grants with the format of xml4
        """
        content=self.getWebContent(self.urlSource_PG_BD)
        htmlP=LinksParser()
        self.links=htmlP.read(content)
        for i in self.links:
            if(self.matchDownload(self.urlPattern_PG_BD_XML4,i)!=None):
                self.fileNames_G_XML4.append(os.path.basename(i))
        print '[get grants (XML4) file names list. Num:{0}]'.format(len(self.fileNames_G_XML4))
        return self.fileNames_G_XML4
    #get the files names of publications
    def getFileNamesPP_XML4(self):
        """
        Used to get all file names of patent publicaitons with the format of xml4
        """
        content=self.getWebContent(self.urlSource_PP_BD)
        htmlP=LinksParser()
        self.links=htmlP.read(content)
        for i in self.links:
            if(self.matchDownload(self.urlPattern_PP_BD_XML4,i)!=None):
                self.fileNames_P_XML4.append(os.path.basename(i))
        print '[get publications (XML4) file names list. Num:{0}]'.format(len(self.fileNames_P_XML4))
        return self.fileNames_P_XML4
    
    def getdLinksPP(self):
        """
        Used to get all downloadable links of Patent Application Publications
        """
        content=self.getWebContent(self.urlSource_PP_BD)
        htmlP=LinksParser()
        self.links=htmlP.read(content)
        for i in self.links:
            if(self.matchDownload(self.urlPattern_PP_BD,i)!=None):
                self.dLinks_PP_BD.append(i)
        print '[get patent applications downloadable links successfully! Num:{0}]'.format(len(self.dLinks_PP_BD))
        return self.dLinks_PP_BD

    def getdLinksPAIR(self):
        """
        Used to get all downloadable links of Patent Application Information Retrieval data
        """
        reader=open(self.urlSource_PAIR,'rb')
        strLines=reader.readlines()
        for s in strLines:
            ls_str=s.replace('-','').split()
            ls_num=[]
            for num in range(int(ls_str[0]),int(ls_str[1])+1):
                ls_num.append(num)
            for num in ls_num:
                strZero=''
                if(num<10000000):
                    for i in range(0,8-len(str(num))):
                        strZero+='0'
                    self.dLinks_PAIR.append(self.urlLinkName_PAIR.replace('[replaceNum]',strZero+str(num)))
                else:
                    self.dLinks_PAIR.append(self.urlLinkName_PAIR.replace('[replaceNum]',str(num)))
        print '[get PAIR data downloadable links successfully! Num:{0}]'.format(len(self.dLinks_PAIR))
        return self.dLinks_PAIR

    def getALLFormats(self):
        """
        get all the formats of grants and publications
        return list
        """
        gXML4='ipgb.*.zip'
        gXML2='pgb.*.zip'
        # the gXML2_4 format data have been already included in the 2001.zip
        # so we don't need to process this format data
        gXML2_4='pgb2001.*.zip'
        # note that most of the aps data are not useful
        # because the "year.zip" contains all the data published weeks
        # gAPS='[0-9]{4}.zip|pba.*.zip'
        # the gXML2_4 format data 2001.zip should be included into the aps format
        gAPS='[0-9]{4}.zip'
        pXML4='ipab.*.zip'
        pXML1='pab.*.zip'
        linkList_G=self.getdLinksPG()
        for link in linkList_G:
            fileName=os.path.basename(link)
            if(self.returnMatch(gXML4,fileName)):
                self.links_G_XML4.append(link)
            elif(self.returnMatch(gXML2,fileName)):
                if(self.returnMatch(gXML2_4,fileName)):
                    self.links_G_XML2_4.append(link)
                else:
                    self.links_G_XML2.append(link)
            elif(self.returnMatch(gAPS,fileName)):
                self.links_G_APS.append(link)
            else:
                #print 'exception for links of grants'
                pass
        print 'gXML4:{0}\ngXML2:{1}\ngXML2_4:{2}\nAPS:{3}'.format(len(self.links_G_XML4),len(self.links_G_XML2),len(self.links_G_XML2_4),len(self.links_G_APS))
        linkList_P=self.getdLinksPP()
        for link in linkList_P:
            fileName=os.path.basename(link)
            if(self.returnMatch(pXML4,fileName)):
                self.links_P_XML4.append(link)
            elif(self.returnMatch(pXML1,fileName)): 
                self.links_P_XML1.append(link)
            else:
                #print 'exception for links of publications'
                pass
        print 'pXML4:{0}\npXML1:{1}'.format(len(self.links_P_XML4),len(self.links_P_XML1))
		
    def getALLFilePaths(self):
        """
        get all the file paths of grants and publications
        return list
        """
        self.files_G_XML4=os.listdir(self.fileDirG_xml4)
        if(len(self.files_G_XML4)>0):
            for i in range(len(self.files_G_XML4)):
                self.files_G_XML4[i]=self.fileDirG_xml4+self.files_G_XML4[i]
                
        self.files_G_XML2=os.listdir(self.fileDirG_xml2)
        if(len(self.files_G_XML2)>0):
            for i in range(len(self.files_G_XML2)):
                self.files_G_XML2[i]=self.fileDirG_xml2+self.files_G_XML2[i]
                
        self.files_G_XML24=os.listdir(self.fileDirG_xml24)
        if(len(self.files_G_XML24)>0):
            for i in range(len(self.files_G_XML24)):
                self.files_G_XML24[i]=self.fileDirG_xml24+self.files_G_XML24[i]
                
        self.files_G_APS=os.listdir(self.fileDirG_aps)
        if(len(self.files_G_APS)>0):
            for i in range(len(self.files_G_APS)):
                self.files_G_APS[i]=self.fileDirG_aps+self.files_G_APS[i]
                
        self.files_P_XML4=os.listdir(self.fileDirP_xml4)
        if(len(self.files_P_XML4)>0):
            for i in range(len(self.files_P_XML4)):
                self.files_P_XML4[i]=self.fileDirP_xml4+self.files_P_XML4[i]
                
        self.files_P_XML1=os.listdir(self.fileDirP_xml1)
        if(len(self.files_P_XML1)>0):
            for i in range(len(self.files_P_XML1)):
                self.files_P_XML1[i]=self.fileDirP_xml1+self.files_P_XML1[i]
        print 'gXML4:{0}\ngXML2:{1}\ngXML2_4:{2}\nAPS:{3}'.format(len(self.files_G_XML4),len(self.files_G_XML2),len(self.files_G_XML24),len(self.files_G_APS))
        print 'pXML4:{0}\npXML1:{1}'.format(len(self.files_P_XML4),len(self.files_P_XML1))


    def getXML4Content(self,dLink='',fileDir=''):
        """
        USED FOR GRANT & PUBLICATION FORMAT: XML4 and upper
        1. download .zip file
        2. generate well-formed .xml file
        3. read .xml file and then return a string to be used by ElementTree
        """
        sTime=time.time()
        self.fileDir=fileDir
        self.fileName=os.path.basename(dLink)
        self.filePath=self.fileDir+'/'+self.fileName
        self.filePathXML=self.filePath+'.xml'
        urllib.urlretrieve(dLink,self.filePath)
        urllib.urlcleanup()
        print '[Downloaded .zip file: {0} Time:{1}]'.format(self.fileName,time.time()-sTime)

        sTime=time.time()
        print '- Starting generate well-formed xml4.'
        import zipfile
        myzip=zipfile.ZipFile(self.filePath,'r')
        fileNameList=myzip.namelist()
        zipfile=myzip.open(fileNameList[0],'r')
        xmlList=[]
        xmlList.insert(0,'<PatentRoot>\r\n')
        for line in zipfile:
            if(line[0:len('<?xml')]!='<?xml' and (line[0:len('<!DOCTYPE')]!='<!DOCTYPE') and (line[0:len('<!ENTITY')]!='<!ENTITY') and (line[0:len(']>')]!=']>')):
                xmlList.append(line)
        myzip.close()
        xmlList.insert(len(xmlList),'</PatentRoot>')
        self.xmlStr=''.join(xmlList)
        #os.remove(self.filePath)
        #xmlFile=open(self.filePath+'.xml','wb') #the most efficient way in comparison with open(path,'w')
        #xmlFile.write(self.xmlStr) #the most efficient way in comparison with writelines(list)
        #xmlFile.close()
        print '[Generated well-formed xml. Time:{0}]'.format(time.time()-sTime)
        return self.xmlStr

    def getXML2Content(self,dLink='',fileDir=''):
        """
        USED FOR GRANT FORMAT: XML2 and upper
        1. download .zip file
        2. generate well-formed .xml file
        3. read .xml file and then return a string to be used by ElementTree
        """
        sTime=time.time()
        self.fileDir=fileDir
        self.fileName=os.path.basename(dLink)
        self.filePath=self.fileDir+'/'+self.fileName
        self.filePathXML=self.filePath+'.xml'
        urllib.urlretrieve(dLink,self.filePath)
        urllib.urlcleanup()
        print '[Downloaded .zip file: {0} Time:{1}]'.format(self.fileName,time.time()-sTime)
        sTime=time.time()
        print '- Starting generating well-formed xml2.'
        import zipfile
        myzip=zipfile.ZipFile(self.filePath,'r')
        for name in myzip.namelist():
            if(name.find('.xml')>-1 or name.find('.sgml')>-1):
                xmlFileName=name
        zipfile=myzip.open(xmlFileName,'r')
        xmlList=[]
        xmlList.insert(0,'<PatentRoot>\r\n')
        for line in zipfile:
            if(line[0:len('<?xml')]!='<?xml' and (line[0:len('<!DOCTYPE')]!='<!DOCTYPE') and (line[0:len('<!ENTITY')]!='<!ENTITY') and (line[0:len(']>')]!=']>')):
                xmlList.append(self.returnRegLine(line))
        myzip.close()
        xmlList.insert(len(xmlList),'</PatentRoot>')
        self.xmlStr=''.join(xmlList)
        #os.remove(self.filePath)
        #xmlFile=open(self.filePath+'.xml','wb') #the most efficient way in comparison with open(path,'w')
        #xmlFile.write(self.xmlStr) #the most efficient way in comparison with writelines(list)
        #xmlFile.close()
        print '[Generated well-formed xml. Time:{0}]'.format(time.time()-sTime)
        return self.xmlStr

    def getXML1Content(self,dLink='',fileDir=''):
        """
        USED FOR PUBLICAITON FORMAT: XML1.0 and upper
        1. download .zip file
        2. generate well-formed .xml file
        3. read .xml file and then return a string to be used by ElementTree
        """
        sTime=time.time()
        self.fileDir=fileDir
        self.fileName=os.path.basename(dLink)
        self.filePath=self.fileDir+'/'+self.fileName
        self.filePathXML=self.filePath+'.xml'
        urllib.urlretrieve(dLink,self.filePath)
        urllib.urlcleanup()
        print '[Downloaded .zip file: {0} Time:{1}]'.format(self.fileName,time.time()-sTime)
        sTime=time.time()
        print '- Starting generating well-formed xml1.'
        import zipfile
        myzip=zipfile.ZipFile(self.filePath,'r')
        for name in myzip.namelist():
            if(name.find('.xml')>-1 or name.find('.sgml')>-1):
                xmlFileName=name
        zipfile=myzip.open(xmlFileName,'r')
        xmlList=[]
        xmlList.insert(0,'<PatentRoot>\r\n')
        for line in zipfile:
            if(line[0:len('<?xml')]!='<?xml' and (line[0:len('<!DOCTYPE')]!='<!DOCTYPE') and (line[0:len('<!ENTITY')]!='<!ENTITY') and (line[0:len(']>')]!=']>')):
                xmlList.append(self.returnRegLine(line))
        myzip.close()
        xmlList.insert(len(xmlList),'</PatentRoot>')
        self.xmlStr=''.join(xmlList)
        #xmlFile=open(self.filePath+'.xml','wb') #the most efficient way in comparison with open(path,'w')
        #xmlFile.write(self.xmlStr) #the most efficient way in comparison with writelines(list)
        #xmlFile.close()
        print '[Generated well-formed xml. Time:{0}]'.format(time.time()-sTime)
        return self.xmlStr

    def getAPSContent(self,dLink='',fileDir=''):
        """
        USED FOR GRANTS FORMAT: APS
        1.download the .zip file
        2.transform the .dat/.txt file into a new preprocessed string list
        3.return the string list (save space to be processed in the memory)
        """
        st=time.time()
        self.fileDir=fileDir
        self.fileName=os.path.basename(dLink)
        self.filePath=self.fileDir+'/'+self.fileName
        urllib.urlretrieve(dLink,self.filePath)
        urllib.urlcleanup()
        print '[Downloaded .zip file: {0} Time:{1}]'.format(self.fileName,time.time()-st)
        st=time.time()
        print '- Starting process APS(.dat or .txt)'
        myzip=zipfile.ZipFile(self.filePath,'r')
        for name in myzip.namelist():
            if(self.returnMatch('.*.dat',name)!=None or self.returnMatch('[a-z]*[0-9]*.txt',name)!=None):
                self.datFileName=name
        datReader=myzip.open(self.datFileName,'r')
        datList=[]
        header=''
        for line in datReader:
            if(len(line.strip())==4):
                datList.append('END|'+header)
                header=line.strip()
                if(header=='PATN'):datList.append('END|***')
            if(len(line[0:4].strip())==0): #append newline
                datList[len(datList)-1]+=' '+line.strip()
            else:datList.append(header+'|'+line.strip())
        datList.append('END|***')
        #datFile=open(self.filePath+'.dat','wb') #the most efficient way in comparison with open(path,'w')
        #datStr='\n'.join(datList)
        #datFile.write(datStr)
        #datFile.close()
        print '[Processed APS(.bat or .txt) File. Length:{0} Time: {1}]'.format(len(datList),time.time()-st)
        #os.remove(self.filePath)
        return datList
		
    def getXML4Content_DPL(self,filePath=''):
        """
        USED FOR GRANT & PUBLICATION FORMAT: XML4 and upper
        1. read .zip file
        2. generate well-formed .xml file
        3. read .xml file and then return a string to be used by ElementTree
        """
        sTime=time.time()
        self.filePath=filePath
        self.xmlStr=''
        print '- Starting generate well-formed xml4.'
        import zipfile
        myzip=zipfile.ZipFile(self.filePath,'r')
        fileNameList=myzip.namelist()
        zipfile=myzip.open(fileNameList[0],'r')
        xmlList=[]
        xmlList.insert(0,'<PatentRoot>\r\n')
        for line in zipfile:
            if(line[0:len('<?xml')]!='<?xml' and (line[0:len('<!DOCTYPE')]!='<!DOCTYPE') and (line[0:len('<!ENTITY')]!='<!ENTITY') and (line[0:len(']>')]!=']>')):
                xmlList.append(line)
        myzip.close()
        xmlList.insert(len(xmlList),'</PatentRoot>')
        self.xmlStr=''.join(xmlList)
        print '[Generated well-formed xml. Time:{0}]'.format(time.time()-sTime)
        return self.xmlStr

    def getXML2Content_DPL(self,filePath=''):
        """
        USED FOR GRANT FORMAT: XML2 and upper
        1. READ .zip file
        2. generate well-formed .xml file
        3. read .xml file and then return a string to be used by ElementTree
        """
        sTime=time.time()
        self.filePath=filePath
        self.xmlStr=''
        print '- Starting generating well-formed xml2.'
        import zipfile
        myzip=zipfile.ZipFile(self.filePath,'r')
        for name in myzip.namelist():
            if(name.find('.xml')>-1 or name.find('.sgml')>-1):
                xmlFileName=name
        zipfile=myzip.open(xmlFileName,'r')
        xmlList=[]
        xmlList.insert(0,'<PatentRoot>\r\n')
        for line in zipfile:
            if(line[0:len('<?xml')]!='<?xml' and (line[0:len('<!DOCTYPE')]!='<!DOCTYPE') and (line[0:len('<!ENTITY')]!='<!ENTITY') and (line[0:len(']>')]!=']>')):
                xmlList.append(self.returnRegLine(line))
        myzip.close()
        xmlList.insert(len(xmlList),'</PatentRoot>')
        self.xmlStr=''.join(xmlList)
        print '[Generated well-formed xml. Time:{0}]'.format(time.time()-sTime)
        return self.xmlStr

    def getXML1Content_DPL(self,filePath=''):
        """
        USED FOR PUBLICAITON FORMAT: XML1.0 and upper
        1. read .zip file
        2. generate well-formed .xml file
        3. read .xml file and then return a string to be used by ElementTree
        """
        sTime=time.time()
        self.filePath=filePath
        self.xmlStr=''
        print '- Starting generating well-formed xml1.'
        import zipfile
        myzip=zipfile.ZipFile(self.filePath,'r')
        for name in myzip.namelist():
            if(name.find('.xml')>-1 or name.find('.sgml')>-1):
                xmlFileName=name
        zipfile=myzip.open(xmlFileName,'r')
        xmlList=[]
        xmlList.insert(0,'<PatentRoot>\r\n')
        for line in zipfile:
            if(line[0:len('<?xml')]!='<?xml' and (line[0:len('<!DOCTYPE')]!='<!DOCTYPE') and (line[0:len('<!ENTITY')]!='<!ENTITY') and (line[0:len(']>')]!=']>')):
                xmlList.append(self.returnRegLine(line))
        myzip.close()
        xmlList.insert(len(xmlList),'</PatentRoot>')
        self.xmlStr=''.join(xmlList)
        print '[Generated well-formed xml. Time:{0}]'.format(time.time()-sTime)
        return self.xmlStr

    def getAPSContent_DPL(self,filePath=''):
        """
        USED FOR GRANTS FORMAT: APS
        1.read the .zip file
        2.transform the .dat/.txt file into a new preprocessed string list
        3.return the string list (save space to be processed in the memory)
        """
        st=time.time()
        self.filePath=filePath
        print '- Starting process APS(.dat or .txt)'
        myzip=zipfile.ZipFile(self.filePath,'r')
        for name in myzip.namelist():
            if(self.returnMatch('.*.dat',name)!=None or self.returnMatch('[a-z]*[0-9]*.txt',name)!=None):
                self.datFileName=name
        datReader=myzip.open(self.datFileName,'r')
        datList=[]
        header=''
        for line in datReader:
            if(len(line.strip())==4):
                datList.append('END|'+header)
                header=line.strip()
                if(header=='PATN'):datList.append('END|***')
            if(len(line[0:4].strip())==0): #append newline
                datList[len(datList)-1]+=' '+line.strip()
            else:datList.append(header+'|'+line.strip())
        datList.append('END|***')
##        if:
##            #in order to process some bad data
##            # in the year of 2006
##            # there are many files only contains one 'blank' line
##            apsPath=myzip.extract(self.datFileName,self.fileDirG_aps)
##            myzip.close()
##            datReader=open(apsPath,'rb')
##            ls=datReader.readlines()
##            lineList=[]
##            for bigLine in ls:
##                for i in range(0,len(bigLine),80):
##                    lineList.append(bigLine[i:i+80])
##            datList=[]
##            header=''
##            for line in lineList:
##                if(len(line.strip())==4):
##                    datList.append('END|'+header)
##                    header=line.strip()
##                    if(header=='PATN'):datList.append('END|***')
##                if(len(line[0:4].strip())==0): #append newline
##                    datList[len(datList)-1]+=' '+line.strip()
##                else:datList.append(header+'|'+line.strip())
##            datList.append('END|***')
        print '[Processed APS(.bat or .txt) File. Length:{0} Time: {1}]'.format(len(datList),time.time()-st)
        return datList

# parse HTML file to get links <a>
class LinksParser(HTMLParser): 
    def __init__(self):
        HTMLParser.__init__(self)

    def read(self,data):
        self._lines=[]
        self.reset()
        self.feed(data)
        return self._lines

    def handle_starttag(self, tag, attrs):   
        if tag == 'a':
            for name,value in attrs:
                if name == 'href':
                    self._lines.append(str(value))
