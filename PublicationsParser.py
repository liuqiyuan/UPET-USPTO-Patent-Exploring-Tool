import xml.etree.ElementTree as ET
import time
import MySQLProcessor
import re
import SourceParser
import os
import multiprocessing
import LogProcessor
import urllib

class PublicationsParser():
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
    Used to parse Patent Applicaiton Publications data and populate them into the database.
    1. obtain contents from SourceParser.py
    2. parse the content and generate .csv files
    3. load .csv files into the database.
    """
    def __init__(self):
        self.pubCountry=''
        self.pubNo=''
        self.kind=''
        self.pubDate=''
        self.appCountry=''
        self.appNo=''
        self.appNoOrig=''
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
        self.pcitationsList=[]  # list of pcitation
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
        self.csvPath_publication=os.getcwd()+'/CSV_P/publications.csv'
        self.csvPath_agent=os.getcwd()+'/CSV_P/agent.csv'
        self.csvPath_assignee=os.getcwd()+'/CSV_P/assignee.csv'
        self.csvPath_examiner=os.getcwd()+'/CSV_P/examiner.csv'
        self.csvPath_intclass=os.getcwd()+'/CSV_P/intclass.csv'
        self.csvPath_inventor=os.getcwd()+'/CSV_P/inventor.csv'
        self.csvPath_pubcit=os.getcwd()+'/CSV_P/pubcit.csv'
        self.csvPath_gracit=os.getcwd()+'/CSV_P/gracit.csv'
        self.csvPath_forpatcit=os.getcwd()+'/CSV_P/forpatcit.csv'
        self.csvPath_nonpatcit=os.getcwd()+'/CSV_P/nonpatcit.csv'
        self.csvPath_usclass=os.getcwd()+'/CSV_P/usclass.csv'

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

    def extractXML4(self,xmlStr):      
        print '- Starting read .xml'
        self.__ResetSQLVariables()
        btime=time.time()
        patentRoot=ET.fromstring(xmlStr)
        #patentRoot=ET.ElementTree().parse('D:\PatentsData\PG_BD\haha.xml')
        print '[Finished read xml. Time:{0}]'.format(time.time()-btime)
        print '- Starting extract .xml'
        btime=time.time()
        # regular info.
        for root in patentRoot.findall('us-patent-application'):
            self.__init__()
            for r in root.findall('us-bibliographic-data-application'):
                for pr in r.findall('publication-reference'):
                    for di in pr.findall('document-id'):
                        self.pubCountry=di.findtext('country')
                        self.pubNo=di.findtext('doc-number')
                        self.kind=di.findtext('kind')
                        self.pubDate=di.findtext('date')
                for ar in r.getiterator('application-reference'):
                    self.appType=ar.attrib['appl-type']
                    for di in ar.findall('document-id'):
                        self.appCountry=di.findtext('country')
                        self.appNo=di.findtext('doc-number')
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
                    for n in nClassFurRoot: #return a list of all subelements
                        self.position+=1
                        self.nClassInfo=n.text
                        self.nClassMain=self.__returnClass(self.nClassInfo)[0]
                        self.nSubclass=self.__returnClass(self.nClassInfo)[1]
                        self.sql_usclass.append([self.pubNo,self.position,self.__returnStr(self.nClassMain),self.__returnStr(self.nSubclass)])                        
                try:
                    self.title=r.findtext('invention-title')
                except:
                    self.title='TITLE ERROR'
                    print '******************************************************************** Title Error **********************************'
                    continue
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
                            self.asnRole=x.find('addressbook').findtext('role')
                            self.asnCity=x.find('addressbook').find('address').findtext('city')
                            self.asnState=x.find('addressbook').find('address').findtext('state')
                            self.asnCountry=x.find('addressbook').find('address').findtext('country')
                            self.sql_assignee.append([self.pubNo,self.position,self.__returnStr(self.asnOrgName),self.asnRole,self.__returnStr(self.asnCity),self.__returnStr(self.asnState),self.__returnStr(self.asnCountry)])
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
            self.sql_publication.append([self.pubNo,self.__returnStr(self.title),self.__returnDate(self.pubDate),self.kind,self.seriesCode,
                                         self.__returnStr(self.abstract),self.__returnInt(self.claimsNum),self.__returnInt(self.drawingsNum),
                                         self.__returnInt(self.figuresNum),self.__returnStr(self.appNo),self.__returnStr(self.claims),
                                         self.__returnDate(self.appDate),self.appType])

        print '===== PUBLICATION ====='
        print len(self.sql_publication)
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

        print '[Extracted .xml. Time:{0}]'.format(time.time()-btime)

    def __returnElementText(self,xmlElement):
        if(ET.iselement(xmlElement)):
            elementStr=ET.tostring(xmlElement)
            return re.sub('<[^<]*>','',elementStr).strip()
        else:return ''

    def extractXML1(self,xmlStr):      
        print '- Starting read .xml'
        self.__ResetSQLVariables()
        btime=time.time()
        patentRoot=ET.fromstring(xmlStr)
        #patentRoot=ET.ElementTree().parse('D:\PatentsData\PG_BD\haha.xml')
        print '[Finished read xml. Time:{0}]'.format(time.time()-btime)
        print '- Starting extract .xml'
        btime=time.time()
        # regular info.
        for root in patentRoot.findall('patent-application-publication'):
            self.__init__()
            for r in root.findall('subdoc-bibliographic-information'):
                for di in r.findall('document-id'):
                    self.pubCountry=''
                    self.pubNo=self.__returnElementText(di.find('doc-number'))
                    self.kind=self.__returnElementText(di.find('kind-code'))
                    self.pubDate=self.__returnElementText(di.find('document-date'))
                self.appType=self.__returnElementText(r.find('publication-filing-type'))
                for ar in r.findall('domestic-filing-data'):
                    self.appCountry=''
                    self.appNo=self.__returnElementText(ar.find('application-number'))
                    self.appDate=self.__returnElementText(ar.find('filing-date'))
                    self.seriesCode=self.__returnElementText(ar.find('application-number-series-code'))
                for cls in r.findall('technical-information'):
                    for ic in cls.findall('classification-ipc'):
                        self.position=1
                        for icm in ic.findall('classification-ipc-primary'):
                            self.iClassCls=self.__returnElementText(icm.find('ipc'))
                            self.sql_intclass.append([self.pubNo,self.position,self.iClassSec,self.iClassCls,self.iClassSub,self.iClassMgr,self.iClassSgr])
                            self.position+=1
                        for ics in ic.findall('classification-ipc-secondary'):
                            self.iClassCls=self.__returnElementText(ics)
                            self.sql_intclass.append([self.pubNo,self.position,self.iClassSec,self.iClassCls,self.iClassSub,self.iClassMgr,self.iClassSgr])
                            self.position+=1
                    for nc in cls.findall('classification-us'):
                        self.position=1
                        for ncp in nc.findall('classification-us-primary'):
                            for uspc in ncp.findall('uspc'):
                                self.nClassCountry=''
                                self.nClassInfo=''
                                self.nClassMain=self.__returnElementText(uspc.find('class'))
                                self.nSubclass=self.__returnElementText(uspc.find('subclass'))
                                self.sql_usclass.append([self.pubNo,self.position,self.__returnStr(self.nClassMain),self.__returnStr(self.nSubclass)])
                                self.position+=1
                        for ncs in nc.findall('classification-us-secondary'):
                            for uspc in ncs.findall('uspc'):
                                self.nClassMain=self.__returnElementText(uspc.find('class'))
                                self.nSubclass=self.__returnElementText(uspc.find('subclass'))
                                self.sql_usclass.append([self.pubNo,self.position,self.__returnStr(self.nClassMain),self.__returnStr(self.nSubclass)])
                                self.position+=1  
                    for ti in cls.findall('title-of-invention'):
                        self.title=self.__returnElementText(ti)
                for iv in r.findall('inventors'):
                    self.position=1
                    for fiv in iv.findall('first-named-inventor'):
                        for n in fiv.findall('name'):
                            self.itFirstName=self.__returnElementText(n.find('given-name'))
                            self.itLastName=self.__returnElementText(n.find('family-name'))
                        for re in fiv.findall('residence'):
                            if(re.find('residence-us')):
                                reu=re.find('residence-us')
                                self.itCity=self.__returnElementText(reu.find('city'))
                                self.itState=self.__returnElementText(reu.find('state'))
                                self.itCountry=self.__returnElementText(reu.find('country-code'))
                            elif(re.find('residence-non-us')):
                                reu=re.find('residence-non-us')
                                self.itCity=self.__returnElementText(reu.find('city'))
                                self.itState=self.__returnElementText(reu.find('state'))
                                self.itCountry=self.__returnElementText(reu.find('country-code'))
                        self.sql_inventor.append([self.pubNo,self.position,self.__returnStr(self.itFirstName),self.__returnStr(self.itLastName),self.__returnStr(self.itCity),self.__returnStr(self.itState),self.__returnStr(self.itCountry),self.__returnStr(self.itNationality),self.__returnStr(self.itResidence)])
                        self.position+=1
                    for ivs in iv.findall('inventor'):
                        for n in ivs.findall('name'):
                            self.itFirstName=self.__returnElementText(n.find('given-name'))
                            self.itLastName=self.__returnElementText(n.find('family-name'))
                        for re in ivs.findall('residence'):
                            if(re.find('residence-us')):
                                reu=re.find('residence-us')
                                self.itCity=self.__returnElementText(reu.find('city'))
                                self.itState=self.__returnElementText(reu.find('state'))
                                self.itCountry=self.__returnElementText(reu.find('country-code'))
                            elif(re.find('residence-non-us')):
                                reu=re.find('residence-non-us')
                                self.itCity=self.__returnElementText(reu.find('city'))
                                self.itState=self.__returnElementText(reu.find('state'))
                                self.itCountry=self.__returnElementText(reu.find('country-code'))
                        self.sql_inventor.append([self.pubNo,self.position,self.__returnStr(self.itFirstName),self.__returnStr(self.itLastName),self.__returnStr(self.itCity),self.__returnStr(self.itState),self.__returnStr(self.itCountry),self.__returnStr(self.itNationality),self.__returnStr(self.itResidence)])
                        self.position+=1
                for assn in r.findall('assignee'):
                    self.position=1
                    for on in assn.findall('organization-name'):
                        self.asnOrgName=self.__returnElementText(on)
                    for ad in assn.findall('address'):
                        self.asnCity=self.__returnElementText(ad.find('city'))
                        self.asnState=self.__returnElementText(ad.find('state'))
                    self.asnRole=self.__returnElementText(assn.find('assignee-type'))
                    self.sql_assignee.append([self.pubNo,self.position,self.__returnStr(self.asnOrgName),self.asnRole,self.__returnStr(self.asnCity),self.__returnStr(self.asnState),self.__returnStr(self.asnCountry)])
                    self.position+=1
                for agn in r.findall('correspondence-address'):
                    self.position=1
                    self.atnOrgName=self.__returnElementText(agn.find('name-1'))
                    for ads in agn.findall('address'):
                        self.atnLastName=''
                        self.atnFirstName=''
                        self.atnCountry=self.__returnElementText(ads.find('country'))
                    self.sql_agent.append([self.pubNo,self.position,self.__returnStr(self.atnOrgName),self.__returnStr(self.atnLastName),self.__returnStr(self.atnFirstName),self.__returnStr(self.atnCountry)])
                    self.position+=1
            for abs in root.findall('subdoc-abstract'):
                self.abstract=self.__returnElementText(abs)

        
            # ****** SQL Variables ********
            self.sql_publication.append([self.pubNo,self.__returnStr(self.title),self.__returnDate(self.pubDate),
                                         self.kind,self.seriesCode,self.__returnStr(self.abstract),self.__returnInt(self.claimsNum),
                                         self.__returnInt(self.drawingsNum),self.__returnInt(self.figuresNum),self.__returnStr(self.appNo),
                                         self.__returnStr(self.claims),
                                         self.__returnDate(self.appDate),self.appType])

        print '===== PUBLICATION ====='
        print len(self.sql_publication)
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

        print '[Extracted .xml. Time:{0}]'.format(time.time()-btime)

    def downloadZIP(self):
        print '- Starting download ZIP files.'
        st=time.time()
        sp=SourceParser.SourceParser()
        sp.getALLFormats()
        ls_xml4=sp.links_P_XML4
        ls_xml1=sp.links_P_XML1
        for dLink in ls_xml4:
            exist_path=(os.getcwd()+'/ZIP_P/XML4/'+os.path.basename(dLink)).replace('\\','/')
            if(not os.path.exists(exist_path)):
                urllib.urlretrieve(dLink,exist_path)
                urllib.urlcleanup()
        for dLink in ls_xml1:
            exist_path=(os.getcwd()+'/ZIP_P/XML1/'+os.path.basename(dLink)).replace('\\','/')
            if(not os.path.exists(exist_path)):
                urllib.urlretrieve(dLink,exist_path)
                urllib.urlcleanup()
        print '[Downloaded ZIP files. Cost: {0}]'.format(time.time()-st)
        
    def writeCSV(self):
        print '- Starting write .csv'
        import csv
        st=time.time()
        self.f_publication=open(self.csvPath_publication,'ab')
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
        w_publication=csv.writer(self.f_publication,delimiter='\t',lineterminator='\n')
        w_publication.writerows(self.sql_publication)
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
        self.f_publication.close()
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

    # wirete csv files_update
    def writeCSV_update(self,suffix):
        print '- Starting write .csv_update'
        import csv
        st=time.time()
        self.f_publication=open(self.csvPath_publication+suffix,'ab')
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
        w_publication=csv.writer(self.f_publication,delimiter='\t',lineterminator='\n')
        w_publication.writerows(self.sql_publication)
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
        self.f_publication.close()
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

        print '***** PUBLICATION *****'
        print self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE uspto_patents.PUBLICATIONS        FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_publication.replace('\\','/')))

        print '***** EXAMINER *****'
        print self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE uspto_patents.EXAMINER_P        FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_examiner.replace('\\','/')))

        print '***** AGENT *****'
        print self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE uspto_patents.AGENT_P      FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_agent.replace('\\','/')))

        print '***** ASSIGNEE *****'
        print self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE uspto_patents.ASSIGNEE_P      FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_assignee.replace('\\','/')))

        print '***** INVENTOR *****'
        print self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE uspto_patents.INVENTOR_P      FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_inventor.replace('\\','/')))

        print '***** PUBCIT *****'
        print self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE uspto_patents.PUBCIT_P      FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_pubcit.replace('\\','/')))

        print '***** GRACIT *****'
        print self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE uspto_patents.GRACIT_P      FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_gracit.replace('\\','/')))

        print '***** FORPATCIT *****'
        print self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE uspto_patents.FORPATCIT_P      FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_forpatcit.replace('\\','/')))

        print '***** NONPATCIT *****'
        print self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE uspto_patents.NONPATCIT_P      FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_nonpatcit.replace('\\','/')))

        print '***** USCLASS *****'
        print self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE uspto_patents.USCLASS_P      FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_usclass.replace('\\','/')))

        print '***** INTCLASS *****'
        print self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE uspto_patents.INTCLASS_P      FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_intclass.replace('\\','/')))

        print self.processor.load("""SET foreign_key_checks = 1;""")
        self.processor.close()
        print '[Loaded .csv. Time:{0}]'.format(time.time()-st)

    def loadCSV_update(self,suffix):
        print '- Starting load CSV files_update.'
        st=time.time()
        self.processor=MySQLProcessor.MySQLProcess()
        self.processor.connect()

        print self.processor.load("""SET foreign_key_checks = 0;""")

        print '***** PUBLICATION *****'
        print self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE uspto_patents.PUBLICATIONS        FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_publication.replace('\\','/')+suffix))

        print '***** EXAMINER *****'
        print self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE uspto_patents.EXAMINER_P        FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_examiner.replace('\\','/')+suffix))

        print '***** AGENT *****'
        print self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE uspto_patents.AGENT_P      FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_agent.replace('\\','/')+suffix))

        print '***** ASSIGNEE *****'
        print self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE uspto_patents.ASSIGNEE_P      FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_assignee.replace('\\','/')+suffix))

        print '***** INVENTOR *****'
        print self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE uspto_patents.INVENTOR_P      FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_inventor.replace('\\','/')+suffix))

        print '***** PUBCIT *****'
        print self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE uspto_patents.PUBCIT_P      FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_pubcit.replace('\\','/')+suffix))

        print '***** GRACIT *****'
        print self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE uspto_patents.GRACIT_P      FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_gracit.replace('\\','/')+suffix))

        print '***** FORPATCIT *****'
        print self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE uspto_patents.FORPATCIT_P      FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_forpatcit.replace('\\','/')+suffix))

        print '***** NONPATCIT *****'
        print self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE uspto_patents.NONPATCIT_P      FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_nonpatcit.replace('\\','/')+suffix))

        print '***** USCLASS *****'
        print self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE uspto_patents.USCLASS_P      FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_usclass.replace('\\','/')+suffix))

        print '***** INTCLASS *****'
        print self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE uspto_patents.INTCLASS_P      FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_intclass.replace('\\','/')+suffix))

        print self.processor.load("""SET foreign_key_checks = 1;""")
        self.processor.close()
        print '[Loaded .csv_update. Time:{0}]'.format(time.time()-st)

# main function for multiprocessing
def mainProcess(fileList,formatStr):
    """
    Parse all the ZIP files into CSV
    """
    print '- Process {0} is starting to work!'.format(os.getpid())
    pst=time.time()
    for filePath in fileList:
        st=time.time()
        fileName=os.path.basename(filePath)
        log=LogProcessor.LogProcess()
        if(formatStr=='xml4'):
            try:
                sp=SourceParser.SourceParser()
                xmlStr=sp.getXML4Content_DPL(filePath)
                p=PublicationsParser()
                p.extractXML4(xmlStr)
                p.writeCSV()
                log.write(log.logPath_P,fileName+'\t'+filePath+'\t'+'XML4'+'\t'+'Processed')
            except:
                log.write(log.logPath_P,fileName+'\t'+filePath+'\t'+'XML4'+'\t'+'Failed')
                continue
        elif(formatStr=='xml1'):
            try:
                sp=SourceParser.SourceParser()
                xmlStr=sp.getXML1Content_DPL(filePath)
                p=PublicationsParser()
                p.extractXML1(xmlStr)
                p.writeCSV()
                log.write(log.logPath_P,fileName+'\t'+filePath+'\t'+'XML1'+'\t'+'Processed')
            except:
                log.write(log.logPath_P,fileName+'\t'+filePath+'\t'+'XML1'+'\t'+'Failed')
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
    parse all the new xml4 zips into csv
    and then load the csv files into the database
    """
    print '- Process {0} is starting to work!'.format(os.getpid())
    st_process=time.time()
    #download new zips
    st_download=time.time()
    p=PublicationsParser()
    p.downloadZIP()
    print '[Downloaded new zips] Cost:{0}'.format(time.time()-st_download)
    #parse and generate csv files
    for fileName in fileNameList:
        st_parse=time.time()
        filePath=(os.getcwd()+'/ZIP_P/XML4/'+fileName).replace('\\','/')
        log=LogProcessor.LogProcess()
        try:
            sp=SourceParser.SourceParser()
            xmlStr=sp.getXML4Content_DPL(filePath)
            p=PublicationsParser()
            p.extractXML4(xmlStr)
            p.writeCSV_update('_update')
            log.write(log.logPath_P,fileName+'\t'+filePath+'\t'+'XML4'+'\t'+'Processed')
        except:
            log.write(log.logPath_P,fileName+'\t'+filePath+'\t'+'XML4'+'\t'+'Failed')
            continue
        print '[Finishing processing one .zip package! Time consuming:{0}]'.format(time.time()-st_parse)
    st_load=time.time()
    p=PublicationsParser()
    p.loadCSV_update('_update')
    print '[Loaded CSV files_update. Cost:{0}]'.format(time.time()-st_load)
    print '[Process {0} is finished. Cost Time:{1}]'.format(os.getpid(),time.time()-st_process)
    
if __name__=="__main__":
    po=PublicationsParser()
    
    #download
    st=time.time()
    po.downloadZIP()
    print '== Downloading Cost: {0} =='.format(time.time()-st)

    #parse
    st=time.time()
    sp=SourceParser.SourceParser()
    sp.getALLFilePaths()
    ls_xml4=sp.files_P_XML4 #396
    ls_xml1=sp.files_P_XML1 #199

    # *** xml1
    processes=[]
    ls_xml1_p=partTen(ls_xml1)
    for fileList in ls_xml1_p:
        processes.append(multiprocessing.Process(target=mainProcess,args=(fileList,'xml1')))
    for p in processes:
        p.start()
    for p in processes:
        p.join()
    print '[Finished all xml1 files]'

    # *** xml4
    processes=[]
    ls_xml4_p=partTen(ls_xml4)
    for fileList in ls_xml4_p:
        processes.append(multiprocessing.Process(target=mainProcess,args=(fileList,'xml4')))
    for p in processes:
        p.start()
    for p in processes:
        p.join()
    print '[Finished all xml4 files]'
    print ('== Parseing Cost:{0} =='.format(time.time()-st))

    #load
    st=time.time()
    po.loadCSV()
    print '== Loading Cost:{0} =='.format(time.time()-st)
