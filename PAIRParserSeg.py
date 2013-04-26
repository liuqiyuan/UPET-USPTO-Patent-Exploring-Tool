import os
import urllib
import zipfile
import re
import MySQLProcessor
import csv
import time
import LogProcessor
import multiprocessing
import SourceParser

class PAIRSeg(object):
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
    This class is used to extract PAIR data and populate them into the database.
    A file named 'PAIRLinks' (~/ID/PAIRLinks) consisting of all available PAIR data downloadable links is generated manually in the beginning 
    in basis of Google Patent USPTO Bulk Downloads website at http://www.google.com/googlebooks/uspto-patents-pair.html .
    """
    def __init__(self):
        self.filePath=os.getcwd().replace('\\','/')+"/ID/PAIRLinks"
        self.dirPath=os.getcwd().replace('\\','/')+'/PAIR'
        self.link=[]  # A range like '08000001 - 08033366'
        self.links=[] # all ranges  2496820 files?
        self.linksStr=[] # http://commondatastorage.googleapis.com/uspto-pair/applications/APP_NUM.zip

        # (correspondence) address and attorney/ agent
        self.aa='' #addressAttorney='' path
        self.aa_Name=''
        self.aa_Address=''
        self.aa_CustomerNum=''
        self.aa_aReg=''
        self.aa_aName=''
        self.aa_aPhone=''

        # application data
        self.ad='' #application data
        self.ad_appNum='' #12/102,391
        self.ad_fileDate=''
        self.ad_appType=''
        self.ad_exmName=''
        self.ad_grpArtUnit=''
        self.ad_confirmNum=''
        self.ad_atyDN='' #attorney docket number
        self.ad_class='' #class/subclasss
        self.ad_firstName=''
        self.ad_customerNum=''
        self.ad_status=''
        self.ad_statusDate=''
        self.ad_location=''
        self.ad_locationDate=''
        self.ad_earlyPubNo=''  #Earliest Publication No	US 2008-0283381 A1 Country:US PubNo.:20080283381 Kind:A1
        self.ad_earlyPubDate=''
        self.ad_patNum='' #7,528,338
        self.ad_issueDate=''
        self.ad_title=''
        self.ad_list=[]

        # continuity data
        self.cd='' #continuity data
        self.cd_desc=''
        self.cd_parentNum=''
        self.cd_parentFileDate=''
        self.cd_parentStatus=''
        self.cd_patentNum=''

        #foreign priority
        self.fp='' #foreign priority
        self.fp_country=''
        self.fp_priority=''
        self.fp_priorityDate=''

        #self.img='' #image file wrapper

        # patent term adjustments
        # *** including two different types:'on or after August 28, 2010' & 'Prior to August 28, 2010'
        self.pta='' #patent term adjustments
        self.pta_priorAfter=1
        # prior
        self.pta_fileDate='' #choose the same field name for prior & after records
        self.pta_issueDate=''
        self.pta_preIssuePetitions=''
        self.pta_postIssuePetitions=''
        self.pta_usptoAdjust=''
        self.pta_usptoDely=''
        self.pta_threeYears=''
        self.pta_appDelay='' #applicant delay days
        self.pta_total='' #total patent term adjustment days
            #* desc
        self.pta_date=''
        self.pta_desc=''
        self.pta_pto=''
        self.pta_appl=''

        # on or after
        self.pta_fileDate=''
        self.pta_issueDate=''
        self.pta_aDelays=''
        self.pta_bDelays=''
        self.pta_cDelays=''
        self.pta_overlap='' #overlapping days between (a&b) or (a&c)
        self.pta_nonOverlap=''
        self.pta_ptoManualAdjust='' #PTO manual adjustments
        self.pta_appDelays='' #applicant delays
        self.pta_total='' #total pta adjustments
            #* desc
        self.pta_number=''
        self.pta_date=''
        self.pta_desc=''
        self.pta_pto=''
        self.pta_appl=''
        self.pta_start=''

        # patent term extension history
        self.pteh='' #patent term extension history
        self.pteh_fileDate=''
        self.pteh_usptoAdjust=''
        self.pteh_usptoDelay=''
        self.pteh_correctDelay=''
        self.pteh_total=''
        self.pteh_date=''
        self.pteh_desc=''
        self.pteh_pto=''
        self.pteh_appl=''

        # transaction history
        self.th='' #transaction history
        self.th_date=''
        self.th_desc=''

        self.position=1

        self.csvPath_applicationpair=os.getcwd().replace('\\','/')+'/CSV_PAIR/application_pair_'
        self.csvPath_attorney=os.getcwd().replace('\\','/')+'/CSV_PAIR/agent_'
        self.csvPath_transaction=os.getcwd().replace('\\','/')+'/CSV_PAIR/transaction_'
        self.csvPath_foreignpriority=os.getcwd().replace('\\','/')+'/CSV_PAIR/foreignpriority_'
        self.csvPath_correspondence=os.getcwd().replace('\\','/')+'/CSV_PAIR/correspondence_'
        self.csvPath_adjustment=os.getcwd().replace('\\','/')+'/CSV_PAIR/adjustment_'
        self.csvPath_adjustmentdesc=os.getcwd().replace('\\','/')+'/CSV_PAIR/adjustmentdesc_'
        self.csvPath_continuity_child=os.getcwd().replace('\\','/')+'/CSV_PAIR/continuity_child_'
        self.csvPath_continuity_parent=os.getcwd().replace('\\','/')+'/CSV_PAIR/continuity_parent_'
        self.csvPath_extension=os.getcwd().replace('\\','/')+'/CSV_PAIR/extension_'
        self.csvPath_extensiondesc=os.getcwd().replace('\\','/')+'/CSV_PAIR/extensiondesc_'

    def __ResetSQLVariables(self):
        # ***** SQL Using *****
        self.sql_application_pair=[]
        self.sql_attorney=[]
        self.sql_transaction=[]
        self.sql_foreignpriority=[]
        self.sql_correspondence=[]
        self.sql_adjustment=[]
        self.sql_adjustmentdesc=[]
        self.sql_continuity_child=[]
        self.sql_continuity_parent=[]
        self.sql_extension=[]
        self.sql_extensiondesc=[]


    # transform string ranges like '08000001 - 08033366' to list
    def TransformToList(self,str):
        ls_str=str.replace('-','').split()
        ls_num=[]
        ls_str2=[]
        for num in range(int(ls_str[0]),int(ls_str[1])+1):
            ls_num.append(num)
        for n in ls_num:
            ls_str2.append(self.AddZero(n))
        return ls_str2

    def AddZero(self,num):
        strZero=''
        if(num<10000001):
            for i in range(0,8-len(str(num))):
                strZero+='0'
            return strZero+str(num)
        else:return str(num)

    # TRANSFORM application number & patent number into FORMAL
    def __TransAppPatNum(self,strNum):
        #remove all the symbols like '/' & ','
        return strNum.replace('/','').replace(',','').strip()
    
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

    def __returnDate(self,s):
        try:
            if(len(s)<8):return '0000-00-00';
            else:
                s=s.strip()
                ss=(s[6:len(s)],s[0:2],s[3:5])
                return '-'.join(ss)
        except:return '0000-00-00'
    
    def ExtractTSV(self,filePath):
        #st=time.time()
        myzip=zipfile.ZipFile(filePath,'r')
        fileNameList=myzip.namelist()
        for n in fileNameList:
            if(re.search('address_and_attorney_agent',n)!=None):self.aa=n
            if(re.search('application_data',n)!=None):self.ad=n
            if(re.search('continuity_data',n)!=None):self.cd=n
            if(re.search('foreign_priority',n)!=None):self.fp=n
            #if(re.search('image_file',n)!=None)
            if(re.search('patent_term_adjustment',n)!=None):self.pta=n
            if(re.search('patent_term_extension_history',n)!=None):self.pteh=n
            if(re.search('transaction_history',n)!=None):self.th=n
            else:pass
        
        # *** application data ***
        if(len(self.ad)>1):
            tsvFile=myzip.open(self.ad,'r')
            tsvFile_ad=tsvFile.readlines()
            self.ad_appNum=self.__TransAppPatNum(tsvFile_ad[0].split('\t')[1])
            self.ad_fileDate=tsvFile_ad[1].split('\t')[1].strip()
            self.ad_appType=tsvFile_ad[2].split('\t')[1].strip()
            self.ad_exmName=tsvFile_ad[3].split('\t')[1].strip()
            self.ad_grpArtUnit=tsvFile_ad[4].split('\t')[1].strip()
            self.ad_confirmNum=tsvFile_ad[5].split('\t')[1].strip()
            self.ad_atyDN=tsvFile_ad[6].split('\t')[1].strip()
            self.ad_class=tsvFile_ad[7].split('\t')[1].strip()
            self.ad_firstName=tsvFile_ad[8].split('\t')[1].strip()
            self.ad_customerNum=tsvFile_ad[9].split('\t')[1].strip()
            self.ad_status=tsvFile_ad[10].split('\t')[1].strip()
            self.ad_statusDate=tsvFile_ad[11].split('\t')[1].strip()
            self.ad_location=tsvFile_ad[12].split('\t')[1].strip()
            self.ad_locationDate=tsvFile_ad[13].split('\t')[1].strip()
            self.ad_earlyPubNo=self.__TransAppPatNum(tsvFile_ad[14].split('\t')[1])
            self.ad_earlyPubDate=tsvFile_ad[15].split('\t')[1].strip()
            self.ad_patNum=self.__TransAppPatNum(tsvFile_ad[16].split('\t')[1])
            self.ad_issueDate=tsvFile_ad[17].split('\t')[1].strip()
            self.ad_title=tsvFile_ad[18].split('\t')[1].strip()
            self.sql_application_pair.append([self.ad_appNum,self.__returnDate(self.ad_fileDate),self.ad_appType
                                              ,self.__returnStr(self.ad_exmName),self.__returnStr(self.ad_grpArtUnit)
                                              ,self.__returnStr(self.ad_confirmNum),self.__returnStr(self.ad_atyDN)
                                              ,self.__returnStr(self.ad_class),self.__returnStr(self.ad_firstName)
                                              ,self.__returnStr(self.ad_customerNum),self.__returnStr(self.ad_status)
                                              ,self.__returnDate(self.ad_statusDate),self.__returnStr(self.ad_location)
                                              ,self.__returnDate(self.ad_locationDate),self.__returnStr(self.ad_earlyPubNo)
                                              ,self.__returnDate(self.ad_earlyPubDate),self.__returnStr(self.ad_patNum)
                                              ,self.__returnDate(self.ad_issueDate),self.__returnStr(self.ad_title)])


        # *** address and attorney/agent ***
        if(len(self.aa)>1):
            tsvFile=myzip.open(self.aa,'r')
            tsvFile_aa=tsvFile.readlines()
            self.aa_Name=tsvFile_aa[0].split('\t')[1]
            self.aa_Address=tsvFile_aa[1].split('\t')[1]
            self.aa_CustomerNum=tsvFile_aa[2].split('\t')[1]
            self.sql_correspondence.append([self.ad_appNum,self.__returnStr(self.aa_Name),self.__returnStr(self.aa_Address),self.__returnStr(self.aa_CustomerNum)])
            if(len(tsvFile_aa)>5):
                self.position=1
                for l in tsvFile_aa[5:len(tsvFile_aa)]:
                    arr=l.split('\t')
                    self.aa_aReg=arr[0].strip()
                    self.aa_aName=arr[1].strip()
                    self.aa_aPhone=arr[2].strip()
                    self.sql_attorney.append([self.ad_appNum
                                              ,self.position
                                              ,self.aa_aReg
                                              ,self.aa_aName.split(',')[0]
                                              ,self.aa_aName.split(',')[1]
                                              ,self.aa_aPhone])
                    self.position+=1

        # *** continuity data ***
        if(len(self.cd)>1):
            tsvFile_cd=myzip.open(self.cd,'r').readlines()
            for line in tsvFile_cd:
                #if(line.find('Description\tParent Number')!=-1):index1=tsvFile_cd.index(line)
                if(line.find('Child Continuity Data')!=-1):index2=tsvFile_cd.index(line)   #str.find() which returns -1 if not found is better than str.index() which returns error
                else:continue
            self.position=1
            for line1 in tsvFile_cd[1:index2-1]:
                ls=line1.split('\t')
                self.cd_desc=ls[0].strip()
                if(len(ls)>1):
                    self.cd_parentNum=ls[1].strip()
                    self.cd_parentFileDate=ls[2].strip()
                    self.cd_parentStatus=ls[3].strip()
                    self.cd_patentNum=ls[4].strip()
                self.sql_continuity_parent.append([self.ad_appNum,
                                                   self.position,
                                                   self.__returnStr(self.cd_desc),
                                                   self.__returnStr(self.cd_parentNum),
                                                   self.__returnDate(self.cd_parentFileDate),
                                                   self.__returnStr(self.cd_parentStatus),
                                                   self.__TransAppPatNum(self.cd_patentNum)])
                self.position+=1
            self.position=1
            for line2 in tsvFile_cd[index2+1:len(tsvFile_cd)]:
                self.sql_continuity_child.append([self.ad_appNum,
                                                  self.position,
                                                  self.__returnStr(line2.strip())])
                self.position+=1
        # *** foreign priority ***
        if(len(self.fp)>1):
            tsvFile_fp=myzip.open(self.fp,'r').readlines()
            self.position=1
            for line in tsvFile_fp[1:len(tsvFile_fp)]:
                self.fp_country=line.split('\t')[0].strip()
                self.fp_priority=line.split('\t')[1].strip()
                self.fp_priorityDate=line.split('\t')[2].strip()
                self.sql_foreignpriority.append([self.ad_appNum,
                                                 self.position,
                                                 self.__returnStr(self.fp_country),
                                                 self.__returnStr(self.fp_priority),
                                                 self.__returnDate(self.fp_priorityDate)])
                self.position+=1
        # *** patent term adjustments ***
        if(len(self.pta)>1):
            tsvFile_pta=myzip.open(self.pta,'r').readlines()
            index_a,index_p=(0,0)
            for line in tsvFile_pta:
                if(line.find('Total PTA Adjustments')!=-1):index_a=tsvFile_pta.index(line)
                if(line.find('Total Patent Term Adjustment (days)')!=-1):index_p=tsvFile_pta.index(line)
            if(index_a==0 and index_p!=0):
                self.position=1
                self.pta_priorAfter=1
                self.pta_fileDate=tsvFile_pta[0].split('\t')[1].strip()
                self.pta_issueDate=tsvFile_pta[1].split('\t')[1].strip()
                self.pta_preIssuePetitions=tsvFile_pta[2].split('\t')[1].strip()
                self.pta_postIssuePetitions=tsvFile_pta[3].split('\t')[1].strip()
                self.pta_usptoAdjust=tsvFile_pta[4].split('\t')[1].strip()
                self.pta_usptoDely=tsvFile_pta[5].split('\t')[1].strip()
                self.pta_threeYears=tsvFile_pta[6].split('\t')[1].strip()
                self.pta_appDelay=tsvFile_pta[7].split('\t')[1].strip()
                self.pta_total=tsvFile_pta[8].split('\t')[1].strip()
                for line in tsvFile_pta[index_p+3:len(tsvFile_pta)]:
                    self.pta_date=line.split('\t')[0]
                    self.pta_desc=line.split('\t')[1]
                    self.pta_pto=line.split('\t')[2]
                    self.pta_appl=line.split('\t')[3]
                    self.sql_adjustmentdesc.append([self.ad_appNum,
                                                    self.position,
                                                    self.pta_priorAfter,
                                                    self.__returnInt(self.pta_number),
                                                    self.__returnDate(self.pta_date),
                                                    self.__returnStr(self.pta_desc),
                                                    self.__returnStr(self.pta_pto),
                                                    self.__returnStr(self.pta_appl),
                                                    self.__returnStr(self.pta_start)])
                    self.position+=1

            elif(index_a!=0 and index_p==0):
                self.position=1
                self.pta_priorAfter=0
                self.pta_fileDate=tsvFile_pta[0].split('\t')[1].strip()
                self.pta_issueDate=tsvFile_pta[1].split('\t')[1].strip()
                self.pta_aDelays=tsvFile_pta[2].split('\t')[1].strip()
                self.pta_bDelays=tsvFile_pta[3].split('\t')[1].strip()
                self.pta_cDelays=tsvFile_pta[4].split('\t')[1].strip()
                self.pta_overlap=tsvFile_pta[5].split('\t')[1].strip()
                self.pta_nonOverlap=tsvFile_pta[6].split('\t')[1].strip()
                self.pta_ptoManualAdjust=tsvFile_pta[7].split('\t')[1].strip()
                self.pta_appDelays=tsvFile_pta[8].split('\t')[1].strip()
                self.pta_total=tsvFile_pta[9].split('\t')[1].strip()
                for line in tsvFile_pta[index_a+3:len(tsvFile_pta)]:
                    self.pta_number=line.split('\t')[0].strip()
                    self.pta_date=line.split('\t')[1].strip()
                    self.pta_desc=line.split('\t')[2].strip()
                    self.pta_pto=line.split('\t')[3].strip()
                    self.pta_appl=line.split('\t')[4].strip()
                    self.pta_start=line.split('\t')[5].strip()
                    self.sql_adjustmentdesc.append([self.ad_appNum,
                                                    self.position,
                                                    self.pta_priorAfter,
                                                    self.__returnInt(self.pta_number),
                                                    self.__returnDate(self.pta_date),
                                                    self.__returnStr(self.pta_desc),
                                                    self.__returnStr(self.pta_pto),
                                                    self.__returnStr(self.pta_appl),
                                                    self.__returnStr(self.pta_start)])
                    self.position+=1
            self.sql_adjustment.append([self.ad_appNum,
                                        self.pta_priorAfter,
                                        self.__returnDate(self.pta_fileDate),
                                        self.__returnDate(self.pta_issueDate),
                                        self.__returnStr(self.pta_preIssuePetitions),
                                        self.__returnStr(self.pta_postIssuePetitions),
                                        self.__returnStr(self.pta_usptoAdjust),
                                        self.__returnStr(self.pta_usptoDely),
                                        self.__returnStr(self.pta_threeYears),
                                        self.__returnStr(self.pta_appDelay),
                                        self.__returnStr(self.pta_total),
                                        self.__returnStr(self.pta_aDelays),
                                        self.__returnStr(self.pta_bDelays),
                                        self.__returnStr(self.pta_cDelays),
                                        self.__returnStr(self.pta_overlap),
                                        self.__returnStr(self.pta_nonOverlap),
                                        self.__returnStr(self.pta_ptoManualAdjust)])
        # *** patent term extension history ***
        if(len(self.pteh)>1):
            tsvFile_pteh=myzip.open(self.pteh,'r').readlines()
            self.pteh_fileDate=tsvFile_pteh[0].split('\t')[1]
            self.pteh_usptoAdjust=tsvFile_pteh[1].split('\t')[1]
            self.pteh_usptoDelay=tsvFile_pteh[2].split('\t')[1]
            self.pteh_correctDelay=tsvFile_pteh[3].split('\t')[1]
            self.pteh_total=tsvFile_pteh[4].split('\t')[1]
            self.sql_extension.append([self.ad_appNum,
                                       self.__returnDate(self.pteh_fileDate),
                                       self.__returnInt(self.pteh_usptoAdjust),
                                       self.__returnInt(self.pteh_usptoDelay),
                                       self.__returnInt(self.pteh_correctDelay),
                                       self.__returnInt(self.pteh_total)])
            self.position=1
            for line in tsvFile_pteh[7:len(tsvFile_pteh)]:
                self.pteh_date=line.split('\t')[0].strip()
                self.pteh_desc=line.split('\t')[1].strip()
                self.pteh_pto=line.split('\t')[2].strip()
                self.pteh_appl=line.split('\t')[3].strip()
                self.sql_extensiondesc.append([self.ad_appNum,
                                               self.position,
                                               self.__returnDate(self.pteh_date),
                                               self.__returnStr(self.pteh_desc),
                                               self.__returnStr(self.pteh_pto),
                                               self.__returnStr(self.pteh_appl)])
                self.position+=1
        # *** transaction history ***
        if(len(self.th)>1):
            self.position=1
            tsvFile_th=myzip.open(self.th,'r').readlines()
            for line in tsvFile_th[1:len(tsvFile_th)]:
                self.th_date=line.split('\t')[0].strip()
                self.th_desc=line.split('\t')[1].strip()
                self.sql_transaction.append([self.ad_appNum,
                                             self.position,
                                             self.__returnStr(self.th_desc),
                                             self.__returnDate(self.th_date)])
                self.position+=1

        myzip.close()
        self.__init__()

        #print 'APP{0},ATN{1},TRA{2},FOR{3},COR{4},ADJ{5},ADJD{6},CONC{7},CONP{8},EXT{9},EXTD{10}'.format(len(self.sql_application_pair),
        #                                                                                                     len(self.sql_attorney),
        #                                                                                                     len(self.sql_transaction),
        #                                                                                                     len(self.sql_foreignpriority),
        #                                                                                                     len(self.sql_correspondence),
        #                                                                                                     len(self.sql_adjustment),
        #                                                                                                     len(self.sql_adjustmentdesc),
        #                                                                                                     len(self.sql_continuity_child),
        #                                                                                                     len(self.sql_continuity_parent),
        #                                                                                                     len(self.sql_extension),
        #                                                                                                     len(self.sql_extensiondesc))

        #print """Extracted FileName:{0}""".format(os.path.basename(filePath))

    def writeCSV(self,linkStrLine):
        addPath=linkStrLine.strip().replace(' - ','_')+'.csv'
        #print 'Getting started to write CSV file...'
        st=time.time()
        self.f_applicationpair=open(self.csvPath_applicationpair+addPath,'wt')
        self.f_attorney=open(self.csvPath_attorney+addPath,'wt')
        self.f_transaction=open(self.csvPath_transaction+addPath,'wt')
        self.f_foreignpriority=open(self.csvPath_foreignpriority+addPath,'wt')
        self.f_correspondence=open(self.csvPath_correspondence+addPath,'wt')
        self.f_adjustment=open(self.csvPath_adjustment+addPath,'wt')
        self.f_adjustmentdesc=open(self.csvPath_adjustmentdesc+addPath,'wt')
        self.f_continuity_child=open(self.csvPath_continuity_child+addPath,'wt')
        self.f_continuity_parent=open(self.csvPath_continuity_parent+addPath,'wt')
        self.f_extension=open(self.csvPath_extension+addPath,'wt')
        self.f_extensiondesc=open(self.csvPath_extensiondesc+addPath,'wt')
        w_applicationpair=csv.writer(self.f_applicationpair,delimiter='\t',lineterminator='\n')
        w_applicationpair.writerows(self.sql_application_pair)
        w_attorney=csv.writer(self.f_attorney,delimiter='\t',lineterminator='\n')
        w_attorney.writerows(self.sql_attorney)
        w_transaction=csv.writer(self.f_transaction,delimiter='\t',lineterminator='\n')
        w_transaction.writerows(self.sql_transaction)
        w_foreignpriority=csv.writer(self.f_foreignpriority,delimiter='\t',lineterminator='\n')
        w_foreignpriority.writerows(self.sql_foreignpriority)
        w_correspondence=csv.writer(self.f_correspondence,delimiter='\t',lineterminator='\n')
        w_correspondence.writerows(self.sql_correspondence)
        w_adjustment=csv.writer(self.f_adjustment,delimiter='\t',lineterminator='\n')
        w_adjustment.writerows(self.sql_adjustment)
        w_adjustmentdesc=csv.writer(self.f_adjustmentdesc,delimiter='\t',lineterminator='\n')
        w_adjustmentdesc.writerows(self.sql_adjustmentdesc)
        w_continuity_child=csv.writer(self.f_continuity_child,delimiter='\t',lineterminator='\n')
        w_continuity_child.writerows(self.sql_continuity_child)
        w_continuity_parent=csv.writer(self.f_continuity_parent,delimiter='\t',lineterminator='\n')
        w_continuity_parent.writerows(self.sql_continuity_parent)
        w_extension=csv.writer(self.f_extension,delimiter='\t',lineterminator='\n')
        w_extension.writerows(self.sql_extension)
        w_extensiondesc=csv.writer(self.f_extensiondesc,delimiter='\t',lineterminator='\n')
        w_extensiondesc.writerows(self.sql_extensiondesc)
        self.f_applicationpair.close()
        self.f_attorney.close()
        self.f_transaction.close()
        self.f_foreignpriority.close()
        self.f_correspondence.close()
        self.f_adjustment.close()
        self.f_adjustmentdesc.close()
        self.f_continuity_child.close()
        self.f_continuity_parent.close()
        self.f_extension.close()
        self.f_extensiondesc.close()
        #print 'Written CSV File. Time:{0}'.format(time.time()-st)
        st=time.time()
        self.processor=MySQLProcessor.MySQLProcess()
        self.processor.connect()

        #print '***** APPLICATION *****'
        self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE qliu14.APPLICATION_PAIR        FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n'
        """.format(filePath=self.csvPath_applicationpair+addPath))

        self.processor.load("""SET foreign_key_checks = 0;""")
        #print '***** ATTORNEY *****'
        self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE qliu14.ATTORNEY        FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_attorney+addPath))

        #print '***** TRANSACTION *****'
        self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE qliu14.TRANSACTION        FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_transaction+addPath))

        #print '***** FOREIGNPRIORITY *****'
        self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE qliu14.FOREIGNPRIORITY      FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_foreignpriority+addPath))
        
        #print '***** CORRESPONDENCE *****'
        self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE qliu14.CORRESPONDENCE      FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_correspondence+addPath))

        #print '***** ADJUSTMENT *****'
        self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE qliu14.ADJUSTMENT     FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_adjustment+addPath))

        #print '***** ADJUSTMENTDESC *****'
        self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE qliu14.ADJUSTMENTDESC      FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_adjustmentdesc+addPath))

        #print '***** CONTINUITY_CHILD *****'
        self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE qliu14.CONTINUITY_CHILD      FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_continuity_child+addPath))

        #print '***** CONTINUITY_PARENT *****'
        self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE qliu14.CONTINUITY_PARENT      FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_continuity_parent+addPath))

        #print '***** EXTENSION *****'
        self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE qliu14.EXTENSION      FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_extension+addPath))

        #print '***** EXTENSIONDESC *****'
        self.processor.load("""LOAD DATA LOCAL INFILE '{filePath}'
        IGNORE INTO TABLE qliu14.EXTENSIONDESC      FIELDS TERMINATED BY '\\t'        OPTIONALLY ENCLOSED BY '\"'        LINES TERMINATED BY '\\n';
        """.format(filePath=self.csvPath_extensiondesc+addPath))

        self.processor.load("""SET foreign_key_checks = 1;""")
        self.processor.close()
        print 'Loaded CSV File. Time:{0}'.format(time.time()-st)
        self.__init__()
        self.__ResetSQLVariables()

def mainProcess(linkList=[]):
    print 'Process {0} is starting to work!'.format(os.getpid())
    st=time.time()
    p=PAIRSeg()
    p._PAIRSeg__ResetSQLVariables()
    log=LogProcessor.LogProcess()
    fNum=os.path.basename(linkList[0]).split('.')[0]
    lNum=os.path.basename(linkList[len(linkList)-1]).split('.')[0]
    numRange=fNum+'-'+lNum
    for link in linkList:
        fileName=os.path.basename(link)
        filePath=p.dirPath+'/'+fileName
        try:
            urllib.urlretrieve(link,filePath)
            #print '[Downloaded .zip File: [{0}]'.format(fileName)
            urllib.urlcleanup()
            zipOrNot=zipfile.is_zipfile(filePath)
            if(zipOrNot==True):
                p.ExtractTSV(filePath)
                os.remove(filePath) # save space on sofus
            elif(zipOrNot==False):
                os.remove(filePath)
            log.write(log.logPath_PAIR,fileName+'\t'+link+'\t'+'PAIR\tProcessed')
        except:
            print 'ERROR: time out. {fileName}'.format(fileName)
            log.write(log.logPath_PAIR_Error,fileName+'\t'+link+'\t'+'PAIR\tProcessed')
    p.writeCSV(numRange)
    print 'Processed range:{range}'.format(range=numRange)
    print '[Process {0} is finished. Populated {1} links. Time:{2}]'.format(os.getpid(),len(linkList),time.time()-st)
    
def partTen(bList):
    n=10
    m=len(bList)
    sList=[bList[0:m/n],bList[m/n:2*m/n],bList[2*m/n:3*m/n],bList[3*m/n:4*m/n],bList[4*m/n:5*m/n],bList[5*m/n:6*m/n],bList[6*m/n:7*m/n],bList[7*m/n:8*m/n],bList[8*m/n:9*m/n],bList[9*m/n:10*m/n]]
    return sList

def multiProcess(allLinkList,numStep):
    for i in range(0,len(allLinkList),numStep):
        st=time.time()
        linkList=allLinkList[i:i+numStep]
        linkListProcesses=partTen(linkList)
        processes=[]    
        for linkList in linkListProcesses:
            processes.append(multiprocessing.Process(target=mainProcess,args=(linkList,)))
        for ps in processes:
            ps.start()
        for ps in processes:
            ps.join()
        print '[multiProcess finished! Time:{time}]'.format(time=time.time()-st)


if __name__=="__main__":
    st=time.time()
    sp=SourceParser.SourceParser()
    allLinkList=sp.getdLinksPAIR()
    multiProcess(allLinkList,1000)

    print 'All PAIR data have been POPULATED successfully! Cost time:{0}'.format(time.time()-st)


