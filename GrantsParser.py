import xml.etree.ElementTree as ET
import time
import MySQLProcessor
import re
import SourceParser
import os
import multiprocessing
import LogProcessor
import urllib


class GrantsParser:
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
    Used to parse Patent Grants data and populate them into the database.
    1. Download
    2. Parse
    3. Load
    """
    def __init__(self):
        self.pubCountry=''
        self.pubNo=''
        self.patNum='' # used to fix patent numbers
        self.kind=''
        self.pubDate=''
        self.appCountry=''
        self.appNo=''
        self.appNoOrig='' #in the APS file, the usseries code corresponds to a different format
        self.appDate=''
        self.appType=''
        self.seriesCode=''

        # priority claims
        self.pcSequence=''
        self.pcKind=''
        self.pcCountry=''
        self.pcDocNum=''
        self.pcDate=''
        self.priClaim=[]
        self.priClaimsList=[]

        # international classification
        self.iClassVersionDate=''
        self.iClassLevel=''
        self.iClassSec='' #section
        self.iClassCls='' #mainclass
        self.iClassSub='' #subclass
        self.iClassMgr='' #main group
        self.iClassSgr='' #subgroup 
        self.iClassSps='' #symbol position
        self.iClassVal='' # classification value
        self.iClassActionDate=''
        self.iClassGnr=''  # generating office
        self.iClassStatus='' #status
        self.iClassDS=''  #data source
        self.iClassList=[]

        #national classification
        self.nClassCountry=''
        self.nClassMain=''
        self.nSubclass=''
        self.nClassInfo=''   #mainClass=nClassInfo[0:3] subClass=nClassInfo[3:len(nClassInfo)]
        self.nClassList=[]

        self.title=''

        # citations
        self.ctNum=''
        self.pctCountry=''  # pct : patent citation
        self.pctDocNo=''
        self.pctKind=''
        self.pctName=''
        self.pctDate=''
        self.pctCategory=''
        self.pctClassNation=''
        self.pctClassMain=''
        self.pctClassList=[]
        self.pcitation=[]
        self.pcitationsList=[]  # list of ALL pcitation
        self.pcitationsList_US=[]
        self.pcitationsList_FC=[]

        self.npctDoc=''
        self.npctCategory=''
        self.npcitation=[]
        self.npcitationsList=[] # list of npcitation

        self.claimsNum=''
        self.figuresNum=''
        self.drawingsNum=''

        # ommit us-related-documents

        # inventors info. 
        self.itSequence=''
        self.itFirstName=''  #it inventor
        self.itLastName=''
        self.itCity=''
        self.itState=''
        self.itCountry=''
        self.itNationality=''
        self.itResidence=''
        self.inventor=[]
        self.inventorsList=[]

        # attorney
        # attorney maybe organizations or, one or more than one person
        self.atnSequence=''
        self.atnLastName=''
        self.atnFirstName=''
        self.atnOrgName=''   
        self.atnCountry=''
        self.attorney=[]
        self.attorneyList=[]
    
        #assignee
        self.asnSequence=''
        self.asnOrgName=''
        self.asnRole=''
        self.asnCity=''
        self.asnState=''
        self.asnCountry=''
        self.assignee=[]
        self.assigneeList=[]

        #examiners
        #primary-examiner & assistant-examiner
        self.exmLastName=''
        self.exmFirstName=''
        self.exmDepartment=''
        self.examiner=[]
        self.examinerList=[]

        self.abstract=''
        self.claims=''
        self.test=''  #used for testing

        self.position=1
        self.count=1

        self.csvPath_grant=os.getcwd()+'/CSV_G/grants.csv'
        self.csvPath_agent=os.getcwd()+'/CSV_G/agent.csv'
        self.csvPath_assignee=os.getcwd()+'/CSV_G/assignee.csv'
        self.csvPath_examiner=os.getcwd()+'/CSV_G/examiner.csv'
        self.csvPath_intclass=os.getcwd()+'/CSV_G/intclass.csv'
        self.csvPath_inventor=os.getcwd()+'/CSV_G/inventor.csv'
        self.csvPath_pubcit=os.getcwd()+'/CSV_G/pubcit.csv'
        self.csvPath_gracit=os.getcwd()+'/CSV_G/gracit.csv'
        self.csvPath_forpatcit=os.getcwd()+'/CSV_G/forpatcit.csv'
        self.csvPath_nonpatcit=os.getcwd()+'/CSV_G/nonpatcit.csv'
        self.csvPath_usclass=os.getcwd()+'/CSV_G/usclass.csv'

    def __ResetSQLVariables(self):
        # ***************** SQL ***************************
        self.sql_publication=[] #publications
        self.sql_grant=[] #grants

        self.sql_examiner=[]
        self.sql_assignee=[]
        self.sql_agent=[]
        self.sql_inventor=[]
        self.sql_usclass=[]
        self.sql_intclass=[]
        self.sql_pubcit=[]  #publication citations
        self.sql_gracit=[] #grant citations
        self.sql_forpatcit=[] #foreign patent citations
        self.sql_nonpatcit=[] #none-patent citations

    def __checkTag(self,x,tagName=''):
        if(x.tag==tagName):
            return True
        else:
            return False

    def __returnClass(self,s='D 2860'):
        """
        Main Class (3):'D02','PLT','000'
        SubClass (3.3): 
        """
        mc=s[0:3].replace(' ','')
        sc=s[3:len(s)]
        sc1=sc[0:3].replace(' ','0')
        sc2=sc[3:len(sc)].replace(' ','')
        if(len(mc)<=3):
            if(mc.find('D')>-1 and len(mc)==2):mc=mc[0]+'0'+mc[1]
            elif(len(mc)==2):mc='0'+mc
            elif(len(mc)==1):mc='00'+mc
        if(len(sc2)<=3):
            if(len(sc2)==2):sc2='0'+sc2
            elif(len(sc2)==1):sc2='00'+sc2
            elif(len(sc2)==0):sc2='000'
        clist=[mc,sc1+sc2]
        return clist

    def __returnDate(self,timeStr):
        if(len(timeStr)>7):
            return timeStr[0:4]+'-'+timeStr[4:6]+'-'+timeStr[6:8]
        else:
            return None

    def __returnInt(self,s):
        try:
            if(s=='' or s==None):return 'NULL';
            else:return int(s)
        except:return 'NULL'

    def __returnStr(self,s):
        try:
            if(s=='' or s==None):return '';
            else:return s.encode('utf-8').replace('"','\'').strip()
        except:return ''

    # ***** used to fix patent numbers *****
    def returnMatch(self,patternStr,inputStr):
        c=re.compile(patternStr)
        r=c.match(inputStr)
        return r

    def returnNewNum(self,oldPatNum):
        if(len(oldPatNum.strip())==9):
            self.patNum=oldPatNum[0:8]
        elif(len(oldPatNum.strip())==8):
            self.patNum=oldPatNum
        else:
            #raw_input('there is patent number whoes legth is nor 8 or 9! It is: {0}'.format(self.patNum))
            pass

        if(self.returnMatch('^[0-9]{8}$',self.patNum)):
            self.patNum=self.patNum[1:8]
            return self.patNum
        else:
            if(self.returnMatch('^[A-Za-z]{1,2}[0-9]{6,7}$',self.patNum)):
                c=re.compile('[0-9]')
                index_0=c.search(self.patNum).start()
                self.patNum=self.patNum[0:index_0]+self.patNum[index_0+1:len(self.patNum)]
                return self.patNum
            else:
                #raw_input('there is patent number out of expection! It is:{0}'.format(self.patNum))
                print 'exception...',oldPatNum
                return ''

    def returnAppNum(self,seriesCode,oldAppNum):
        if(str.upper(seriesCode.strip())=='D'):
            seriesCode='29'
        if(len(seriesCode.strip())==1):
            seriesCode='0'+seriesCode
        elif(len(seriesCode.strip())==0):
            seriesCode='xx'
        if(len(oldAppNum)==7):
            oldAppNum=oldAppNum[0:6]
        return seriesCode+oldAppNum       
            
    def extractXML4(self,xmlStr):      
        print '[Getting started to read xml into ElementTree...]'
        self.__ResetSQLVariables()
        btime=time.time()
        patentRoot=ET.fromstring(xmlStr)
        #patentRoot=ET.ElementTree().parse('D:\PatentsData\PG_BD\haha.xml')
        print '[Finishing reading xml file into ElementTree, consuming time:{0}]'.format(time.time()-btime)
        print '[Getting started to parse XML and extract metadata...'
        btime=time.time()
        # regular info.
        for root in patentRoot.findall('us-patent-grant'):
            self.__init__()
            for r in root.findall('us-bibliographic-data-grant'):
                for pr in r.findall('publication-reference'):
                    for di in pr.findall('document-id'):
                        self.pubCountry=di.findtext('country')
                        self.pubNo=di.findtext('doc-number')
                        self.pubNo=self.returnNewNum(self.pubNo)
                        self.kind=di.findtext('kind')
                        self.pubDate=di.findtext('date')
                for ar in r.getiterator('application-reference'):
                    self.appType=ar.attrib['appl-type']
                    for di in ar.findall('document-id'):
                        self.appCountry=di.findtext('country')
                        self.appNo=di.findtext('doc-number')
                        self.appNoOrig=self.appNo
                        self.appDate=di.findtext('date')
                self.seriesCode=r.findtext('us-application-series-code')
                #for pc in r.findall('priority-claims'):
                #    for pcs in pc.getiterator('priority-claim'):
                #        self.pcSequence=pcs.attrib['sequence']
                #        self.pcKind=pcs.attrib['kind']
                #        self.pcCountry=pcs.findtext('country')
                #        self.pcDocNum=pcs.findtext('doc-number')
                #        self.pcDate=pcs.findtext('date')
                #        self.priClaim=[self.pcSequence,self.pcKind,self.pcCountry,self.pcDocNum,self.pcDate]
                #        self.priClaimsList.append(self.priClaim)
                for ic in r.findall('classifications-ipcr'):
                    self.position=1
                    for icc in ic.findall('classification-ipcr'):
                        for ivi in icc.findall('ipc-version-indicator'):
                            self.iClassVersionDate=ivi.findtext('date')
                        for ad in icc.getiterator('action-date'):
                            self.iClassActionDate=ad.findtext('date')
                        for go in icc.findall('generating-office'):
                            self.iClassGnr=go.findtext('country')
                        for x in icc.getchildren():
                            if(self.__checkTag(x,'classification-level')):self.iClassLevel=x.text
                            if(self.__checkTag(x,'section')):self.iClassSec=x.text
                            if(self.__checkTag(x,'class')):self.iClassCls=x.text
                            if(self.__checkTag(x,'subclass')):self.iClassSub=x.text
                            if(self.__checkTag(x,'main-group')):self.iClassMgr=x.text
                            if(self.__checkTag(x,'subgroup')):self.iClassSgr=x.text
                            if(self.__checkTag(x,'symbol-position')): self.iClassSps=x.text
                            if(self.__checkTag(x,'classification-value')):self.iClassVal=x.text
                            if(self.__checkTag(x,'classfication-status')):self.iClassStatus=x.text
                            if(self.__checkTag(x,'classification-date-source')):self.iClassDS=x.text
                        #self.iClassList.append([self.pubNo,self.position,self.iClassSec,self.iClassCls,self.iClassSub,self.iClassMgr,self.iClassSgr])
                        self.sql_intclass.append([self.pubNo,self.position,self.iClassSec,self.iClassCls,self.iClassSub,self.iClassMgr,self.iClassSgr])
                        self.position+=1
                for nc in r.findall('classification-national'):
                    self.position=1
                    self.nClassCountry=nc.findtext('country')
                    self.nClassInfo=nc.findtext('main-classification')
                    self.nClassMain=self.__returnClass(self.nClassInfo)[0]
                    self.nSubclass=self.__returnClass(self.nClassInfo)[1]
                    self.sql_usclass.append([self.pubNo,self.position,self.__returnStr(self.nClassMain),self.__returnStr(self.nSubclass)])
                    nClassFurRoot=nc.findall('further-classification') #return a list of all elements
                    for n in nClassFurRoot:
                        self.position+=1
                        self.nClassInfo=n.text
                        self.nClassMain=self.__returnClass(self.nClassInfo)[0]
                        self.nSubclass=self.__returnClass(self.nClassInfo)[1]
                        self.sql_usclass.append([self.pubNo,self.position,self.__returnStr(self.nClassMain),self.__returnStr(self.nSubclass)])                        
                self.title=r.findtext('invention-title')
                for rf in r.findall('references-cited'):
                    for rfc in rf.findall('citation'):
                        if(rfc.find('patcit')!=None):
                            self.ctNum=rfc.find('patcit').attrib['num']
                            for x in rfc.findall('patcit'):
                                self.pctCountry=x.find('document-id').findtext('country')
                                self.pctDocNo=x.find('document-id').findtext('doc-number')
                                self.pctKind=x.find('document-id').findtext('kind')
                                self.pctName=x.find('document-id').findtext('name')
                                self.pctDate=x.find('document-id').findtext('date')
                            self.pctCategory=rfc.findtext('category')
                            #us patent citations
                            if(self.pctCountry.strip().upper()=='US'):
                                if(self.pctDocNo.find('/')>-1):
                                    self.sql_pubcit.append([self.pubNo,self.ctNum,self.pctDocNo,self.pctKind,self.__returnStr(self.pctName),self.__returnDate(self.pctDate),self.pctCountry,self.__returnStr(self.pctCategory)])
                                else:
                                    self.sql_gracit.append([self.pubNo,self.ctNum,self.pctDocNo,self.pctKind,self.__returnStr(self.pctName),self.__returnDate(self.pctDate),self.pctCountry,self.__returnStr(self.pctCategory)])
                            elif(self.pctCountry.strip().upper()!='US'):
                                self.sql_forpatcit.append([self.pubNo,self.ctNum,self.pctDocNo,self.pctKind,self.__returnStr(self.pctName),self.__returnDate(self.pctDate),self.pctCountry,self.__returnStr(self.pctCategory)])
                        elif(rfc.find('nplcit')!=None):
                            self.ctNum=rfc.find('nplcit').attrib['num']
                            # sometimes, there will be '<i> or <sup>, etc.' in the reference string; we need to remove it
                            self.npctDoc=ET.tostring(rfc.find('nplcit').find('othercit'))
                            self.npctDoc=re.sub('<[^>]+>','',self.npctDoc).rstrip('\n')
                            self.npctCategory=rfc.findtext('category')
                            self.sql_nonpatcit.append([self.pubNo,self.ctNum,self.__returnStr(self.npctDoc),self.__returnStr(self.npctCategory)])
                self.claimsNum=r.findtext('number-of-claims')
                for nof in r.findall('figures'):
                    self.drawingsNum=nof.findtext('number-of-drawing-sheets')
                    self.figuresNum=nof.findtext('number-of-figures')
                for prt in r.findall('parties'):
                    for apts in prt.findall('applicants'):
                        for apt in apts.findall('applicant'):
                            self.itSequence=apt.attrib['sequence']
                            if(apt.find('addressbook')!=None):
                                self.itFirstName=apt.find('addressbook').findtext('first-name')
                                self.itLastName=apt.find('addressbook').findtext('last-name')
                                self.itCity=apt.find('addressbook').find('address').findtext('city')
                                self.itState=apt.find('addressbook').find('address').findtext('state')
                                self.itCountry=apt.find('addressbook').find('address').findtext('country')
                                self.itNationality=apt.find('nationality').findtext('country')
                                self.itResidence=apt.find('residence').findtext('country')
                                self.sql_inventor.append([self.pubNo,self.itSequence,self.__returnStr(self.itFirstName),self.__returnStr(self.itLastName),self.__returnStr(self.itCity),self.__returnStr(self.itState),self.__returnStr(self.itCountry),self.__returnStr(self.itNationality),self.__returnStr(self.itResidence)])
                    for agns in prt.findall('agents'):
                        for agn in agns.findall('agent'):
                            self.asnSequence=agn.attrib['sequence']
                            if(agn.find('addressbook')!=None):
                                self.atnOrgName=agn.find('addressbook').findtext('orgname')
                                self.atnLastName=agn.find('addressbook').findtext('last-name')
                                self.atnFirstName=agn.find('addressbook').findtext('first-name')
                                self.atnCountry=agn.find('addressbook').find('address').findtext('country')
                                self.sql_agent.append([self.pubNo,self.asnSequence,self.__returnStr(self.atnOrgName),self.__returnStr(self.atnLastName),self.__returnStr(self.atnFirstName),self.__returnStr(self.atnCountry)])
                for asn in r.findall('assignees'):
                    self.position=1
                    for x in asn.findall('assignee'):
                        if(x.find('addressbook')!=None):
                            self.asnOrgName=x.find('addressbook').findtext('orgname')
                            self.asnRle=x.find('addressbook').findtext('role')
                            self.asnCity=x.find('addressbook').find('address').findtext('city')
                            self.asnState=x.find('addressbook').find('address').findtext('state')
                            self.asnCountry=x.find('addressbook').find('address').findtext('country')
                            self.sql_assignee.append([self.pubNo,self.position,self.__returnStr(self.asnOrgName),self.asnRle,self.__returnStr(self.asnCity),self.__returnStr(self.asnState),self.__returnStr(self.asnCountry)])
                            self.position+=1
                for exm in r.findall('examiners'):
                    for x in exm.findall('primary-examiner'):
                        self.exmLastName=x.findtext('last-name')
                        self.exmFirstName=x.findtext('first-name')
                        self.exmDepartment=x.findtext('department')
                        self.sql_examiner.append([self.pubNo,1,self.__returnStr(self.exmLastName),self.__returnStr(self.exmFirstName),self.__returnStr(self.exmDepartment)])
                    for x in exm.findall('assistant-examiner'):
                        self.exmLastName=x.findtext('last-name')
                        self.exmFirstName=x.findtext('first-name')
                        self.exmDepartment=x.findtext('department')
                        self.sql_examiner.append([self.pubNo,2,self.__returnStr(self.exmLastName),self.__returnStr(self.exmFirstName),self.__returnStr(self.exmDepartment)])
            #self.abstract=root.findtext('abstract')
            for abs in root.findall('abstract'):
                self.abstract=re.sub('<[^>]+>','',ET.tostring(abs)).strip()

            # ****** SQL Variables ********
            self.sql_grant.append([self.pubNo,self.__returnStr(self.title),
                                   self.__returnDate(self.pubDate),
                                   self.kind,
                                   self.seriesCode,
                                   self.__returnStr(self.abstract),
                                   self.__returnInt(self.claimsNum),
                                   self.__returnInt(self.drawingsNum),
                                   self.__returnInt(self.figuresNum),
                                   self.__returnStr(self.appNo),
                                   self.__returnStr(self.claims),
                                   self.__returnDate(self.appDate),
                                   self.appType,
                                   self.appNoOrig])

        print '===== GRANT ====='
        print len(self.sql_grant)
        print '===== EXAMINER ====='
        print len(self.sql_examiner)
        print '===== ASSIGNEE ====='
        print len(self.sql_assignee)
        print '=====  AGENT ====='
        print len(self.sql_agent)
        print '===== INVENTOR ====='
        print len(self.sql_inventor)
        print '===== USCLASS ====='
        print len(self.sql_usclass)
        print '===== INTCLASS ====='
        print len(self.sql_intclass)
        print '===== PUBCIT ====='
        print len(self.sql_pubcit)
        print '===== GRACIT ====='
        print len(self.sql_gracit)
        print '===== FORPATCIT ====='
        print len(self.sql_forpatcit)
        print '===== NONPATCIT ====='
        print len(self.sql_nonpatcit)

            #text=raw_input('press Y/y to continue!')
            #if(text=='Y' or text=='y'):continue
            #else:break
        print '[Finishing parsing XML to extract metadata, consuming time:{0}]'.format(time.time()-btime)

    def __returnElementText(self,xmlElement):
        if(ET.iselement(xmlElement)):
            elementStr=ET.tostring(xmlElement)
            return re.sub('<[^<]*>','',elementStr).strip()
        else:return ''

    def extractXML2(self,xmlStr):   
        """
        used for Patent Grant Bibliographic Data/XML Version 2.5 (Text Only)
        from 2002 - 2004
        A subset of the Patent Grant Data/XML (a.k.a., Grant Red Book) XML with 'B' tags
        """
        print 'Starting read xml.'
        self.__ResetSQLVariables()
        btime=time.time()
        patentRoot=ET.fromstring(xmlStr)
        print '[Finishing reading XML, Time:{0}]'.format(time.time()-btime)
        print 'Starting extract xml.'
        btime=time.time()
        for root in patentRoot.findall('PATDOC'): # us-patent-grant'):
            self.__init__()
            for r in root.findall('SDOBI'): #us-bibliographic-data-grant'):
                for B100 in r.findall('B100'): #PUBLICATION
                    self.pubNo=self.__returnElementText(B100.find('B110'))
                    self.pubNo=self.returnNewNum(self.pubNo)
                    self.kind=self.__returnElementText(B100.find('B130'))
                    self.pubDate=self.__returnElementText(B100.find('B140'))
                    self.pubCountry=self.__returnElementText(B100.find('B190'))
                for B200 in r.findall('B200'): # APPLICATION
                    self.appType=''
                    self.appCountry=''
                    self.appNo=self.__returnElementText(B200.find('B210'))
                    self.appNoOrig=self.appNo
                    self.appDate=self.__returnElementText(B200.find('B220'))
                    self.seriesCode=self.__returnElementText(B200.find('B211US'))
                for B500 in r.findall('B500'):
                    for B520 in B500.findall('B520'): #US CLASSIFICATION
                        for B521 in B520.findall('B521'): # USCLASS MAIN
                            self.nClassInfo=self.__returnElementText(B521)
                            self.nClassMain=self.__returnClass(self.nClassInfo)[0]
                            self.nSubclass=self.__returnClass(self.nClassInfo)[1]
                            self.sql_usclass.append([self.pubNo,1,self.__returnStr(self.nClassMain),self.__returnStr(self.nSubclass)])
                        self.position=2
                        for B522 in B520.findall('B522'): # USCLASS FURTHER
                            self.nClassInfo=self.__returnElementText(B522)
                            self.nClassMain=self.__returnClass(self.nClassInfo)[0]
                            self.nSubclass=self.__returnClass(self.nClassInfo)[1]
                            self.sql_usclass.append([self.pubNo,self.position,self.__returnStr(self.nClassMain),self.__returnStr(self.nSubclass)])
                            self.position+=1
                    for B510 in B500.findall('B510'): # INTERNATIONAL CLASS
                        for B511 in B510.findall('B511'): #MAIN CLASS
                            self.iClassVersionDate=''
                            self.iClassActionDate=''
                            self.iClassGnr=''
                            self.iClassLevel=''
                            self.iClassSec=''
                            intClass=self.__returnElementText(B511)
                            if(len(intClass.split())>1):
                                self.iClassCls=intClass.split()[0]
                                self.iClassSub=intClass.split()[1]
                            else:
                                self.iClassCls=intClass
                                self.iClassSub=''
                            self.iClassMgr=''
                            self.iClassSgr=''
                            self.iClassSps=''
                            self.iClassVal=''
                            self.iClassStatus=''
                            self.iClassDS=''
                            self.sql_intclass.append([self.pubNo,1,self.iClassSec,self.iClassCls,self.iClassSub,self.iClassMgr,self.iClassSgr])
                        self.position=2
                        for B512 in B510.findall('B511'): #INTERNATIONAL CLASS FURTHER
                            self.iClassVersionDate=''
                            self.iClassActionDate=''
                            self.iClassGnr=''
                            self.iClassLevel=''
                            self.iClassSec=''
                            intClass=self.__returnElementText(B512)
                            if(len(intClass.split())>1):
                                self.iClassCls=intClass.split()[0]
                                self.iClassSub=intClass.split()[1]
                            else:
                                self.iClassCls=intClass
                                self.iClassSub=''
                            self.iClassMgr=''
                            self.iClassSgr=''
                            self.iClassSps=''
                            self.iClassVal=''
                            self.iClassStatus=''
                            self.iClassDS=''
                            self.sql_intclass.append([self.pubNo,self.position,self.iClassSec,self.iClassCls,self.iClassSub,self.iClassMgr,self.iClassSgr])
                            self.position+=1
                    for B540 in B500.findall('B540'):
                        self.title=self.__returnElementText(B540) #TITLE
                    for B560 in B500.findall('B560'): # CITATIONS
                        self.position=1
                        for B561 in B560.findall('B561'): #PATCIT
                            for PCIT in B561.findall('PCIT'):
                                self.ctNum=self.position
                                self.pctCountry=''
                                for DOC in PCIT.findall('DOC'):
                                    self.pctDocNo=self.__returnElementText(DOC.find('DNUM'))
                                    self.pctKind=self.__returnElementText(DOC.find('KIND'))
                                    self.pctDate=self.__returnElementText(DOC.find('DATE'))
                                self.pctName=self.__returnElementText(PCIT.find('PARTY-US'))
                            if(len(B561.getchildren())>1):
                                self.pctCategory=B561.getchildren()[1].tag
                            else:self.pctCategory=''
                            if(self.pctDocNo.find('/')>-1 and self.pctDocNo.find(' ')==-1):
                                self.sql_pubcit.append([self.pubNo,self.position,self.pctDocNo,self.pctKind,self.__returnStr(self.pctName),self.__returnDate(self.pctDate),self.pctCountry,self.__returnStr(self.pctCategory)])
                            elif(self.pctDocNo.find('/')==-1 and self.pctDocNo.find(' ')==-1):
                                self.sql_gracit.append([self.pubNo,self.position,self.pctDocNo,self.pctKind,self.__returnStr(self.pctName),self.__returnDate(self.pctDate),self.pctCountry,self.__returnStr(self.pctCategory)])
                            else:
                                self.sql_forpatcit.append([self.pubNo,self.position,self.pctDocNo,self.pctKind,self.__returnStr(self.pctName),self.__returnDate(self.pctDate),self.pctCountry,self.__returnStr(self.pctCategory)])
                            self.position+=1
                        self.position=1
                        for B562 in B560.findall('B562'): #NON-PATENT LITERATURE
                            for NCIT in B562.findall('NCIT'):
                                # sometimes, there will be '<i> or <sup>, etc.' in the reference string; we need to remove it
                                self.npctDoc=self.__returnElementText(NCIT)
                                self.npctDoc=re.sub('<[^>]+>','',self.npctDoc)
                                self.npctCategory=ET.tostring(NCIT)
                                if(len(B562.getchildren())>1):
                                    self.npctCategory=B562.getchildren()[1].tag
                            self.sql_nonpatcit.append([self.pubNo,self.position,self.__returnStr(self.npctDoc),self.__returnStr(self.npctCategory)])
                            self.position+=1
                    for B570 in B500.findall('B570'):
                        self.claimsNum=self.__returnElementText(B570.find('B577'))
                    for B590 in B500.findall('B590'):
                        for B595 in B590.findall('B595'):
                            self.drawingsNum=self.__returnElementText(B595)
                        for B596 in B590.findall('B596'):
                            self.figuresNum=self.__returnElementText(B596)
                for B700 in r.findall('B700'): #PARTIES
                    for B720 in B700.findall('B720'): #INVENTOR
                        self.position=1
                        for B721 in B720.findall('B721'):
                            for i in B721.findall('PARTY-US'):
                                self.itSequence=self.position
                                self.itFirstName=self.__returnElementText(i.find('NAM').find('FNM'))
                                self.itLastName=self.__returnElementText(i.find('NAM').find('SNM'))
                                self.itCity=self.__returnElementText(i.find('ADR').find('CITY'))
                                self.itState=self.__returnElementText(i.find('ADR').find('STATE'))
                                self.itCountry=self.__returnElementText(i.find('ADR').find('CTRY'))
                                self.itNationality=''
                                self.itResidence=''
                            self.sql_inventor.append([self.pubNo,self.position,self.__returnStr(self.itFirstName),self.__returnStr(self.itLastName),self.__returnStr(self.itCity),self.__returnStr(self.itState),self.__returnStr(self.itCountry),self.__returnStr(self.itNationality),self.__returnStr(self.itResidence)])
                            self.position+=1
                    for B730 in B700.findall('B730'): #ASSIGNEE
                        self.position=1
                        for B731 in B730.findall('B731'):
                            for x in B731.findall('PARTY-US'):
                                self.asnOrgName=self.__returnElementText(x.find('NAM'))
                                self.asnRole=''
                                for ADR in x.findall('ADR'):
                                    self.asnCity=self.__returnElementText(ADR.find('CITY'))
                                    self.asnState=self.__returnElementText(ADR.findall('STATE'))
                                    self.asnCountry=self.__returnElementText(ADR.findall('CTRY'))
                            self.sql_assignee.append([self.pubNo,self.position,self.__returnStr(self.asnOrgName),self.asnRole,self.__returnStr(self.asnCity),self.__returnStr(self.asnState),self.__returnStr(self.asnCountry)])
                            self.position+=1
                    for B740 in B700.findall('B740'): #AGENT
                        self.position=1
                        for B741 in B740.findall('B741'):
                            for x in B741.findall('PARTY-US'):
                                self.asnSequence=self.position
                                self.atnOrgName=self.__returnElementText(x.find('NAM'))
                                self.atnLastName=''
                                self.atnFirstName=''
                                self.atnCountry=''
                            self.sql_agent.append([self.pubNo,self.asnSequence,self.__returnStr(self.atnOrgName),self.__returnStr(self.atnLastName),self.__returnStr(self.atnFirstName),self.__returnStr(self.atnCountry)])
                    for B745 in B700.findall('B745'): #PERSON ACTING UPON THE DOC
                        for B746 in B745.findall('B746'): #PRIMARY EXAMINER
                            for x in B746.findall('PARTY-US'):
                                self.exmLastName=self.__returnElementText(x.find('NAM').find('SNM'))
                                self.exmFirstName=self.__returnElementText(x.find('NAM').find('FNM'))
                                self.exmDepartment=''
                                self.sql_examiner.append([self.pubNo,1,self.__returnStr(self.exmLastName),self.__returnStr(self.exmFirstName),self.__returnStr(self.exmDepartment)])
                        for B747 in B745.findall('B747'): #ASSISTANT EXAMINER
                            for x in B747.findall('PARTY-US'):
                                self.exmLastName=self.__returnElementText(x.find('NAM').find('SNM'))
                                self.exmFirstName=self.__returnElementText(x.find('NAM').find('FNM'))
                                self.exmDepartment=''
                                self.sql_examiner.append([self.pubNo,2,self.__returnStr(self.exmLastName),self.__returnStr(self.exmFirstName),self.__returnStr(self.exmDepartment)])
            for abs in root.findall('SDOCL'):
                self.abstract=self.__returnElementText(abs)

            # ****** SQL Variables ********
            self.sql_grant.append([self.pubNo,self.__returnStr(self.title),self.__returnDate(self.pubDate),
                                   self.kind,self.seriesCode,self.__returnStr(self.abstract),self.__returnInt(self.claimsNum),
                                   self.__returnInt(self.drawingsNum),self.__returnInt(self.figuresNum),
                                   self.__returnStr(self.appNo),
                                   self.__returnStr(self.claims),
                                   self.__returnDate(self.appDate),
                                   self.appType,
                                   self.__returnStr(self.appNo)])

        print '===== GRANT ====='
        print len(self.sql_grant)
        print '===== EXAMINER ====='
        print len(self.sql_examiner)
        print '===== ASSIGNEE ====='
        print len(self.sql_assignee)
        print '=====  AGENT ====='
        print len(self.sql_agent)
        print '===== INVENTOR ====='
        print len(self.sql_inventor)
        print '===== USCLASS ====='
        print len(self.sql_usclass)
        print '===== INTCLASS ====='
        print len(self.sql_intclass)
        print '===== PUBCIT ====='
        print len(self.sql_pubcit)
        print '===== GRACIT ====='
        print len(self.sql_gracit)
        print '===== FORPATCIT ====='
        print len(self.sql_forpatcit)
        print '===== NONPATCIT ====='
        print len(self.sql_nonpatcit)
        print '[Finishing parsing XML to extract metadata, consuming time:{0}]'.format(time.time()-btime)

    def extractAPS(self,strList=[]):
        print '- Starting extract APS'
        st=time.time()
        self.__ResetSQLVariables()
        for line in strList:
            header=line[0:9].strip()
            #BASIC INFO.
            if(header=='PATN|PATN'):
                self.__init__()
                self.position_invt=0
                self.position_uclas=0
                self.position_iclas=0
                self.position_assg=0
                self.position_uref=0
                self.position_fref=0
                self.position_oref=0
                self.position_lrep=0
            if(header=='PATN|WKU'):
                self.pubNo=line[9:len(line)].strip()
                self.pubNo=self.returnNewNum(self.pubNo)
            elif(header=='PATN|SRC'):
                self.seriesCode=line[9:len(line)].strip()
            elif(header=='PATN|APN'):
                self.appNoOrig=line[9:len(line)].strip()
                self.appNo=self.returnAppNum(self.seriesCode,self.appNoOrig)
            elif(header=='PATN|APT'):
                self.appType=line[9:len(line)].strip()
            elif(header=='PATN|APD'):
                self.appDate=line[9:len(line)].strip()
            elif(header=='PATN|TTL'):
                self.title=line[9:len(line)].strip()
            elif(header=='PATN|ISD'):
                self.pubDate=line[9:len(line)].strip()
            #EXAMINER
            elif(header=='PATN|EXP'):
                self.examinerPri=line[9:len(line)].strip()
                if(self.examinerPri.find(';')>-1):
                    self.sql_examiner.append([self.pubNo,1,self.__returnStr(self.examinerPri.split(';')[0]),self.__returnStr(self.examinerPri.split(';')[1]),self.__returnStr(self.exmDepartment)])
                else:
                    self.sql_examiner.append([self.pubNo,1,self.__returnStr(self.examinerPri),self.__returnStr(''),self.__returnStr(self.exmDepartment)])
            elif(header=='PATN|EXA'):
                self.examinerAst=line[9:len(line)].strip()
                if(self.examinerAst.find(';')>-1):
                    self.sql_examiner.append([self.pubNo,2,self.__returnStr(self.examinerAst.split(';')[0]),self.__returnStr(self.examinerAst.split(';')[1]),self.__returnStr(self.exmDepartment)])
                else:
                    self.sql_examiner.append([self.pubNo,2,self.__returnStr(self.examinerAst),self.__returnStr(''),self.__returnStr(self.exmDepartment)])
            elif(header=='PATN|NCL'):self.claimsNum=line[9:len(line)].strip()
            elif(header=='PATN|NDR'):self.drawingsNum=line[9:len(line)].strip()
            elif(header=='PATN|NFG'):self.figuresNum=line[9:len(line)].strip()

            #INVENTOR
            elif(header=='INVT|INVT'):
                self.itResidence=''
                self.itCity=''
                self.itState=''
                self.itCountry=''
                self.itFirstName=''
                self.itLastName=''
                self.position_invt+=1
            elif(header=='INVT|STR'):
                self.itResidence=line[9:len(line)].strip()
            elif(header=='INVT|CTY'):
                self.itCity=line[9:len(line)].strip()
            elif(header=='INVT|STA'):
                self.itState=line[9:len(line)].strip()
            elif(header=='INVT|CNT'):
                self.itCountry=line[9:len(line)].strip()
            elif(header=='INVT|NAM'):
                name=line[9:len(line)].strip()
                if(name.find(';')>-1):
                    self.itFirstName=name.split(';')[1]
                    self.itLastName=name.split(';')[0]
                else:self.itLastName=name
            elif(header=='END|INVT'):
                self.sql_inventor.append([self.pubNo,self.position_invt,self.__returnStr(self.itFirstName),self.__returnStr(self.itLastName),self.__returnStr(self.itCity),self.__returnStr(self.itState),self.__returnStr(self.itCountry),self.__returnStr(self.itNationality),self.__returnStr(self.itResidence)])

            #ASSIGNEE
            elif(header=='ASSG|ASSG'):
                self.asnCity=''
                self.asnCountry=''
                self.asnOrgName=''
                self.position_assg+=1
            elif(header=='ASSG|CTY'):
                self.asnCity=line[9:len(line)].strip()
            elif(header=='ASSG|CNT'):
                self.asnCountry=line[9:len(line)].strip()
            elif(header=='ASSG|NAM'):
                self.asnOrgName=line[9:len(line)].strip()
            elif(header=='END|ASSG'):
                self.sql_assignee.append([self.pubNo,self.position,self.__returnStr(self.asnOrgName),self.asnRole,self.__returnStr(self.asnCity),self.__returnStr(self.asnState),self.__returnStr(self.asnCountry)])

            #CLASSIFICATION
            elif(header=='CLAS|CLAS'):pass
            elif(header=='CLAS|OCL'):
                self.position_uclas+=1
                self.nClassInfo=line[10:len(line)].rstrip() # remindre: right strip
                self.nClassMain=self.__returnClass(self.nClassInfo)[0]
                self.nSubclass=self.__returnClass(self.nClassInfo)[1]
                self.sql_usclass.append([self.pubNo,self.position_uclas,self.__returnStr(self.nClassMain),self.__returnStr(self.nSubclass)])
            elif(header=='CLAS|XCL'):
                self.position_uclas+=1
                self.nClassInfo=line[10:len(line)].rstrip() # remindre: right strip
                self.nClassMain=self.__returnClass(self.nClassInfo)[0]
                self.nSubclass=self.__returnClass(self.nClassInfo)[1]
                self.sql_usclass.append([self.pubNo,self.position_uclas,self.__returnStr(self.nClassMain),self.__returnStr(self.nSubclass)])
            elif(header=='CLAS|ICL'):
                self.position_iclas+=1
                self.iClassCls=line[10:len(line)].rstrip() # remindre: right strip
                self.sql_intclass.append([self.pubNo,self.position_iclas,self.iClassSec,self.iClassCls,self.iClassSub,self.iClassMgr,self.iClassSgr])

            #CITATIONS
            elif(header=='UREF|UREF'):
                self.pctDocNo=''
                self.pctDate=''
                self.pctName=''
                self.position_uref+=1
            elif(header=='UREF|PNO'):
                self.pctDocNo=line[9:len(line)].strip()
            elif(header=='UREF|ISD'):
                self.pctDate=line[9:len(line)].strip()
            elif(header=='UREF|NAM'):
                self.pctName=line[9:len(line)].strip()
            elif(header=='END|UREF'):
                if(self.pctDocNo.find('/')==-1 and self.pctDocNo.find(' ')==-1):
                    self.sql_gracit.append([self.pubNo,self.position_uref,self.pctDocNo,self.pctKind,self.__returnStr(self.pctName),self.__returnDate(self.pctDate),self.pctCountry,self.__returnStr(self.pctCategory)])
                else:
                    self.sql_pubcit.append([self.pubNo,self.position_uref,self.pctDocNo,self.pctKind,self.__returnStr(self.pctName),self.__returnDate(self.pctDate),self.pctCountry,self.__returnStr(self.pctCategory)])

            #FOREIGN REFERENCES
            elif(header=='FREF|FREF'):
                self.pctDocNo=''
                self.pctDate=''
                self.pctCountry=''
                self.position_fref+=1
            elif(header=='FREF|PNO'):
                self.pctDocNo=line[9:len(line)].strip()
            elif(header=='FREF|ISD'):
                self.pctDate=line[9:len(line)].strip()
            elif(header=='FREF|CNT'):
                self.pctCountry=line[9:len(line)].strip()
            elif(header=='END|FREF'):
                self.sql_forpatcit.append([self.pubNo,self.position_fref,self.pctDocNo,self.pctKind,self.__returnStr(self.pctName),self.__returnDate(self.pctDate),self.pctCountry,self.__returnStr(self.pctCategory)])

            #OTHER REFERENCES
            elif(header=='OREF|OREF'):
                pass
            elif(header=='OREF|PAL'):
                self.position_oref+=1
                self.npctDoc=line[9:len(line)].strip()
                self.sql_nonpatcit.append([self.pubNo,self.position_oref,self.__returnStr(self.npctDoc),self.__returnStr(self.npctCategory)])

            #AGENT
            elif(header=='LREP|FRM'):
                self.position_lrep+=1
                self.atnOrgName=line[9:len(line)].strip()
                self.sql_agent.append([self.pubNo,self.position_lrep,self.__returnStr(self.atnOrgName),self.__returnStr(self.atnLastName),self.__returnStr(self.atnFirstName),self.__returnStr(self.atnCountry)])
            elif(header=='LREP|FR2'):
                self.position_lrep+=1
                name=line[9:len(line)].strip()
                if(name.find(';')>-1):
                    self.atnLastName=name.split(';')[0]
                    self.atnFirstName=name.split(';')[1]
                    self.sql_agent.append([self.pubNo,self.position_lrep,self.__returnStr(''),self.__returnStr(self.atnLastName),self.__returnStr(self.atnFirstName),self.__returnStr(self.atnCountry)])

            #ABSTRACT
            elif(header=='DCLM|PAL'):
                self.claims=line[9:len(line)].strip()
            elif(header=='ABST|PAL'):
                self.abstract=line[9:len(line)].strip()

            elif(header=='END|***'):
                # ****** SQL Variables ********
                if(len(self.pubNo)>1):
                    #self.sql_application.append([self.__returnStr(self.appNo),self.__returnDate(self.appDate),self.appType])
                    self.sql_grant.append([self.pubNo,self.__returnStr(self.title),self.__returnDate(self.pubDate),self.kind,self.seriesCode,
                                           self.__returnStr(self.abstract),self.__returnInt(self.claimsNum),self.__returnInt(self.drawingsNum),
                                           self.__returnInt(self.figuresNum),
                                           self.__returnStr(self.appNo),
                                           self.__returnStr(self.claims),
                                           self.__returnDate(self.appDate),
                                           self.appType,
                                           self.appNoOrig])
        print '===== GRANTS ====='
        print len(self.sql_grant)
        print '===== EXAMINER ====='
        print len(self.sql_examiner)
        print '===== ASSIGNEE ====='
        print len(self.sql_assignee)
        print '=====  AGENT ====='
        print len(self.sql_agent)
        print '===== INVENTOR ====='
        print len(self.sql_inventor)
        print '===== USCLASS ====='
        print len(self.sql_usclass)
        print '===== INTCLASS ====='
        print len(self.sql_intclass)
        print '===== PUBCIT ====='
        print len(self.sql_pubcit)
        print '===== GRACIT ====='
        print len(self.sql_gracit)
        print '===== FORPATCIT ====='
        print len(self.sql_forpatcit)
        print '===== NONPATCIT ====='
        print len(self.sql_nonpatcit)
        print '[Extracted APS. Time:{0}'.format(time.time()-st)

    def downloadZIP(self):
        print '- Starting download ZIP files.'
        st=time.time()
        sp=SourceParser.SourceParser()
        sp.getALLFormats()
        ls_xml4=sp.links_G_XML4  #396 412
        ls_xml2=sp.links_G_XML2 #157
        ls_xml24=sp.links_G_XML2_4 #52
        ls_aps=sp.links_G_APS #252 final 26
        for dLink in ls_xml4:
            exist_path=(os.getcwd()+'/ZIP_G/XML4/'+os.path.basename(dLink)).replace('\\','/')
            if(not os.path.exists(exist_path)):
               urllib.urlretrieve(dLink,exist_path)
               urllib.urlcleanup()
        for dLink in ls_xml2:
            exist_path=(os.getcwd()+'/ZIP_G/XML2/'+os.path.basename(dLink)).replace('\\','/')
            if(not os.path.exists(exist_path)):
                urllib.urlretrieve(dLink,exist_path)
                urllib.urlcleanup()
        for dLink in ls_xml24:
            exist_path=(os.getcwd()+'/ZIP_G/XML24/'+os.path.basename(dLink)).replace('\\','/')
            if(not os.path.exists(exist_path)):
                urllib.urlretrieve(dLink,exist_path)
                urllib.urlcleanup()
        for dLink in ls_aps:
            exist_path=(os.getcwd()+'/ZIP_G/APS/'+os.path.basename(dLink)).replace('\\','/')
            if(not os.path.exists(exist_path)):
                urllib.urlretrieve(dLink,exist_path)
                urllib.urlcleanup()
        print '[Downloaded ZIP files. Cost: {0}]'.format(time.time()-st)
		
    def writeCSV(self):
        print '- Starting write CSV files.'
        import csv
        st=time.time()
        self.f_grant=open(self.csvPath_grant,'ab')
        self.f_examiner=open(self.csvPath_examiner,'ab')
        self.f_agent=open(self.csvPath_agent,'ab')
        self.f_assignee=open(self.csvPath_assignee,'ab')
        self.f_inventor=open(self.csvPath_inventor,'ab')
        self.f_pubcit=open(self.csvPath_pubcit,'ab')
        self.f_gracit=open(self.csvPath_gracit,'ab')
        self.f_forpatcit=open(self.csvPath_forpatcit,'ab')
        self.f_nonpatcit=open(self.csvPath_nonpatcit,'ab')
        self.f_usclass=open(self.csvPath_usclass,'ab')
        self.f_intclass=open(self.csvPath_intclass,'ab')
        w_grant=csv.writer(self.f_grant,delimiter='\t',lineterminator='\n')
        w_grant.writerows(self.sql_grant)
        w_examiner=csv.writer(self.f_examiner,delimiter='\t',lineterminator='\n')
        w_examiner.writerows(self.sql_examiner)
        w_agent=csv.writer(self.f_agent,delimiter='\t',lineterminator='\n')
        w_agent.writerows(self.sql_agent)
        w_assignee=csv.writer(self.f_assignee,delimiter='\t',lineterminator='\n')
        w_assignee.writerows(self.sql_assignee)
        w_inventor=csv.writer(self.f_inventor,delimiter='\t',lineterminator='\n')
        w_inventor.writerows(self.sql_inventor)
        w_pubcit=csv.writer(self.f_pubcit,delimiter='\t',lineterminator='\n')
        w_pubcit.writerows(self.sql_pubcit)
        w_gracit=csv.writer(self.f_gracit,delimiter='\t',lineterminator='\n')
        w_gracit.writerows(self.sql_gracit)
        w_forpatcit=csv.writer(self.f_forpatcit,delimiter='\t',lineterminator='\n')
        w_forpatcit.writerows(self.sql_forpatcit)
        w_nonpatcit=csv.writer(self.f_nonpatcit,delimiter='\t',lineterminator='\n')
        w_nonpatcit.writerows(self.sql_nonpatcit)
        w_usclass=csv.writer(self.f_usclass,delimiter='\t',lineterminator='\n')
        w_usclass.writerows(self.sql_usclass)
        w_intclass=csv.writer(self.f_intclass,delimiter='\t',lineterminator='\n')
        w_intclass.writerows(self.sql_intclass)
        self.f_grant.close()
        self.f_examiner.close()
        self.f_agent.close()
        self.f_assignee.close()
        self.f_inventor.close()
        self.f_pubcit.close()
        self.f_gracit.close()
        self.f_forpatcit.close()
        self.f_nonpatcit.close()
        self.f_usclass.close()
        self.f_intclass.close()
        self.__ResetSQLVariables()
        print '[Written CSV files. Cost:{0}]'.format(time.time()-st)

    #write csv files for updating
    def writeCSV_update(self,suffix):
        print '- Starting write CSV files_update.'
        import csv
        st=time.time()
        self.f_grant=open(self.csvPath_grant+suffix,'ab')
        self.f_examiner=open(self.csvPath_examiner+suffix,'ab')
        self.f_agent=open(self.csvPath_agent+suffix,'ab')
        self.f_assignee=open(self.csvPath_assignee+suffix,'ab')
        self.f_inventor=open(self.csvPath_inventor+suffix,'ab')
        self.f_pubcit=open(self.csvPath_pubcit+suffix,'ab')
        self.f_gracit=open(self.csvPath_gracit+suffix,'ab')
        self.f_forpatcit=open(self.csvPath_forpatcit+suffix,'ab')
        self.f_nonpatcit=open(self.csvPath_nonpatcit+suffix,'ab')
        self.f_usclass=open(self.csvPath_usclass+suffix,'ab')
        self.f_intclass=open(self.csvPath_intclass+suffix,'ab')
        w_grant=csv.writer(self.f_grant,delimiter='\t',lineterminator='\n')
        w_grant.writerows(self.sql_grant)
        w_examiner=csv.writer(self.f_examiner,delimiter='\t',lineterminator='\n')
        w_examiner.writerows(self.sql_examiner)
        w_agent=csv.writer(self.f_agent,delimiter='\t',lineterminator='\n')
        w_agent.writerows(self.sql_agent)
        w_assignee=csv.writer(self.f_assignee,delimiter='\t',lineterminator='\n')
        w_assignee.writerows(self.sql_assignee)
        w_inventor=csv.writer(self.f_inventor,delimiter='\t',lineterminator='\n')
        w_inventor.writerows(self.sql_inventor)
        w_pubcit=csv.writer(self.f_pubcit,delimiter='\t',lineterminator='\n')
        w_pubcit.writerows(self.sql_pubcit)
        w_gracit=csv.writer(self.f_gracit,delimiter='\t',lineterminator='\n')
        w_gracit.writerows(self.sql_gracit)
        w_forpatcit=csv.writer(self.f_forpatcit,delimiter='\t',lineterminator='\n')
        w_forpatcit.writerows(self.sql_forpatcit)
        w_nonpatcit=csv.writer(self.f_nonpatcit,delimiter='\t',lineterminator='\n')
        w_nonpatcit.writerows(self.sql_nonpatcit)
        w_usclass=csv.writer(self.f_usclass,delimiter='\t',lineterminator='\n')
        w_usclass.writerows(self.sql_usclass)
        w_intclass=csv.writer(self.f_intclass,delimiter='\t',lineterminator='\n')
        w_intclass.writerows(self.sql_intclass)
        self.f_grant.close()
        self.f_examiner.close()
        self.f_agent.close()
        self.f_assignee.close()
        self.f_inventor.close()
        self.f_pubcit.close()
        self.f_gracit.close()
        self.f_forpatcit.close()
        self.f_nonpatcit.close()
        self.f_usclass.close()
        self.f_intclass.close()
        self.__ResetSQLVariables()
        print '[Written CSV files_update. Cost:{0}]'.format(time.time()-st)
	
    def loadCSV(self):
        print '- Starting load CSV files.'
        st=time.time()
        self.processor=MySQLProcessor.MySQLProcess()
        self.processor.connect()

        print self.processor.load("""SET foreign_key_checks = 0;""")

        print '***** GRANT *****'
        print self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE uspto_patents.GRANTS        FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_grant.replace('\\','/')))

        print '***** EXAMINER *****'
        print self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE uspto_patents.EXAMINER_G        FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_examiner.replace('\\','/')))

        print '***** AGENT *****'
        print self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE uspto_patents.AGENT_G      FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_agent.replace('\\','/')))

        print '***** ASSIGNEE *****'
        print self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE uspto_patents.ASSIGNEE_G      FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_assignee.replace('\\','/')))

        print '***** INVENTOR *****'
        print self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE uspto_patents.INVENTOR_G      FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_inventor.replace('\\','/')))

        print '***** PUBCIT *****'
        print self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE uspto_patents.PUBCIT_G      FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_pubcit.replace('\\','/')))

        print '***** GRACIT *****'
        print self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE uspto_patents.GRACIT_G      FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_gracit.replace('\\','/')))

        print '***** FORPATCIT *****'
        print self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE uspto_patents.FORPATCIT_G      FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_forpatcit.replace('\\','/')))

        print '***** NONPATCIT *****'
        print self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE uspto_patents.NONPATCIT_G      FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_nonpatcit.replace('\\','/')))

        print '***** USCLASS *****'
        print self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE uspto_patents.USCLASS_G      FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_usclass.replace('\\','/')))

        print '***** INTCLASS *****'
        print self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE uspto_patents.INTCLASS_G      FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_intclass.replace('\\','/')))

        print self.processor.load("""SET foreign_key_checks = 1;""")
        self.processor.close()
        print '[Loaded CSV files. Time:{0}'.format(time.time()-st)

    #loda csv files _update    
    def loadCSV_update(self,suffix):
        print '- Starting load CSV files_update.'
        st=time.time()
        self.processor=MySQLProcessor.MySQLProcess()
        self.processor.connect()

        print self.processor.load("""SET foreign_key_checks = 0;""")

        print '***** GRANT *****'
        print self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE uspto_patents.GRANTS        FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_grant.replace('\\','/')+suffix))

        print '***** EXAMINER *****'
        print self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE uspto_patents.EXAMINER_G        FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_examiner.replace('\\','/')+suffix))

        print '***** AGENT *****'
        print self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE uspto_patents.AGENT_G      FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_agent.replace('\\','/')+suffix))

        print '***** ASSIGNEE *****'
        print self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE uspto_patents.ASSIGNEE_G      FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_assignee.replace('\\','/')+suffix))

        print '***** INVENTOR *****'
        print self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE uspto_patents.INVENTOR_G      FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_inventor.replace('\\','/')+suffix))

        print '***** PUBCIT *****'
        print self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE uspto_patents.PUBCIT_G      FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_pubcit.replace('\\','/')+suffix))

        print '***** GRACIT *****'
        print self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE uspto_patents.GRACIT_G      FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_gracit.replace('\\','/')+suffix))

        print '***** FORPATCIT *****'
        print self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE uspto_patents.FORPATCIT_G      FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_forpatcit.replace('\\','/')+suffix))

        print '***** NONPATCIT *****'
        print self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE uspto_patents.NONPATCIT_G      FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_nonpatcit.replace('\\','/')+suffix))

        print '***** USCLASS *****'
        print self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE uspto_patents.USCLASS_G      FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_usclass.replace('\\','/')+suffix))

        print '***** INTCLASS *****'
        print self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE uspto_patents.INTCLASS_G      FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_intclass.replace('\\','/')+suffix))

        print self.processor.load("""SET foreign_key_checks = 1;""")
        self.processor.close()
        print '[Loaded CSV files_update. Time:{0}'.format(time.time()-st)

# main function for multiprocessing
def mainProcess(fileList,formatStr):
    """
    Parse all the ZIP files into CSV
    """
    print 'Process {0} is starting to work!'.format(os.getpid())
    pst=time.time()
    for filePath in fileList:
        st=time.time()
        fileName=os.path.basename(filePath)
        log=LogProcessor.LogProcess()
        if(formatStr=='aps'):
            try:
                sp=SourceParser.SourceParser()
                datFilePath=sp.getAPSContent_DPL(filePath)
                g=GrantsParser()
                g.extractAPS(datFilePath)
                g.writeCSV()
                log.write(log.logPath_G,fileName+'\t'+filePath+'\t'+'APS'+'\t'+'Processed')
            except:
                log.write(log.logPath_G,fileName+'\t'+filePath+'\t'+'APS'+'\t'+'Failed')
                continue
        elif(formatStr=='xml4'):
            try:
                sp=SourceParser.SourceParser()
                xmlStr=sp.getXML4Content_DPL(filePath)
                g=GrantsParser()
                g.extractXML4(xmlStr)
                g.writeCSV()
                log.write(log.logPath_G,fileName+'\t'+filePath+'\t'+'XML4'+'\t'+'Processed')
            except:
                log.write(log.logPath_G,fileName+'\t'+filePath+'\t'+'XML4'+'\t'+'Failed')
                continue
        elif(formatStr=='xml2'):
            try:
                sp=SourceParser.SourceParser()
                xmlStr=sp.getXML2Content_DPL(filePath)
                g=GrantsParser()
                g.extractXML2(xmlStr)
                g.writeCSV()
                log.write(log.logPath_G,fileName+'\t'+filePath+'\t'+formatStr+'\t'+'Processed')
            except:
                log.write(log.logPath_G,fileName+'\t'+filePath+'\t'+formatStr+'\t'+'Failed')
                continue
        elif(formatStr=='xml24'):
            try:
                sp=SourceParser.SourceParser()
                xmlStr=sp.getXML2Content_DPL(filePath)
                g=GrantsParser()
                g.extractXML2(xmlStr)
                g.writeCSV()
                log.write(log.logPath_G,fileName+'\t'+filePath+'\t'+formatStr+'\t'+'Processed')
            except:
                log.write(log.logPath_G,fileName+'\t'+filePath+'\t'+formatStr+'\t'+'Failed')
                continue
        print '[Finishing processing one .zip package! Time consuming:{0}]'.format(time.time()-st)
    print '[Process {0} is finished. Cost Time:{1}]'.format(os.getpid(),time.time()-pst)
    
def partTen(bList):
    n=10
    m=len(bList)
    sList=[bList[0:m/n],bList[m/n:2*m/n],bList[2*m/n:3*m/n],bList[3*m/n:4*m/n],bList[4*m/n:5*m/n],bList[5*m/n:6*m/n],bList[6*m/n:7*m/n],bList[7*m/n:8*m/n],bList[8*m/n:9*m/n],bList[9*m/n:10*m/n]]
    return sList

# main function for autoUpdater
def update(fileNameList):
    """
    Parse all the new xml4 ZIP files into CSV
    and then load the CSV files into the database
    """
    print 'Process {0} is starting to work!'.format(os.getpid())
    st_process=time.time()
    #download new zips
    st_download=time.time()
    g=GrantsParser()
    g.downloadZIP()
    print '[Downloaded new zips] Cost:{0}'.format(time.time()-st_download)
    #parse and generate csv files
    for fileName in fileNameList:
        st_parse=time.time()
        filePath=(os.getcwd()+'/ZIP_G/XML4/'+fileName).replace('\\','/')
        log=LogProcessor.LogProcess()
        try:
            sp=SourceParser.SourceParser()
            xmlStr=sp.getXML4Content_DPL(filePath)
            g=GrantsParser()
            g.extractXML4(xmlStr)
            g.writeCSV_update('_update')
            log.write(log.logPath_G,fileName+'\t'+filePath+'\t'+'XML4'+'\t'+'Processed')
        except:
            log.write(log.logPath_G,fileName+'\t'+filePath+'\t'+'XML4'+'\t'+'Failed')
            continue
        print '[Finishing processing one .zip package! Time consuming:{0}]'.format(time.time()-st_parse)
    st_load=time.time()
    g=GrantsParser()
    g.loadCSV_update('_update')
    print '[Loaded CSV files_update. Cost:{0}]'.format(time.time()-st_load)
    print '[Process {0} is finished. Cost Time:{1}]'.format(os.getpid(),time.time()-st_process)

if __name__=="__main__":
    g=GrantsParser()

    #download
    st=time.time()
    g.downloadZIP()
    print '== Downloading Cost: {0} =='.format(time.time()-st)
    
    #parse
    st=time.time()
    sp=SourceParser.SourceParser()
    sp.getALLFilePaths()
    ls_xml4=sp.files_G_XML4  #396
    ls_xml2=sp.files_G_XML2 #157
    ls_xml24=sp.files_G_XML24 #52
    ls_aps=sp.files_G_APS #252

    # *** aps
    processes=[]
    ls_aps_p=partTen(ls_aps)
    for fileList in ls_aps_p:
        processes.append(multiprocessing.Process(target=mainProcess,args=(fileList,'aps')))
    for p in processes:
        p.start()
    for p in processes:
        p.join()

    # *** xml4
    processes=[]
    ls_xml4_p=partTen(ls_xml4)
    for fileList in ls_xml4_p:
        processes.append(multiprocessing.Process(target=mainProcess,args=(fileList,'xml4')))
    for p in processes:
        p.start()
    for p in processes:
        p.join()

    # *** xml2
    processes=[]
    ls_xml2_p=partTen(ls_xml2)
    for fileList in ls_xml2_p:
        processes.append(multiprocessing.Process(target=mainProcess,args=(fileList,'xml2')))
    for p in processes:
        p.start()
    for p in processes:
        p.join()
        
# XML2_4 format data has been included in 2001.zip.
# they are not necessaryly reprocessed.
##    # *** xml24
##    processes=[]
##    ls_xml24_p=[ls_xml24[0:20],ls_xml24[20:40],ls_xml24[40:len(ls_xml24)]]
##    for fileList in ls_xml24_p:
##        processes.append(multiprocessing.Process(target=mainProcess,args=(fileList,'xml24')))
##    for p in processes:
##        p.start()
##    for p in processes:
##        p.join()
    
    print '== Parsing Cost:{0} =='.format(time.time()-st)

    #load
    st=time.time()
    g.loadCSV()
    print '== Loading Cost:{0} =='.format(time.time()-st)
