import os

class ClassificationParser(object):
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
    Used to parse Classification data and insert them into the database.
    processing data:"U.S. Manual of Classification File (CTAF, Classification Text Attribute File)/ctaf1204.txt"
    """

    def __init__(self):
        self.cls=''
        self.subcls=''
        self.indent=''
        self.subclsSeqNum=''
        self.nextHigSub=''
        self.title=''
        self.clsList=[]

    def GetClasses(self,filePath):
        reader=open(filePath,'r')
        readerList=reader.readlines()
        for line in readerList:
            self.cls=line[0:3]
            self.subcls=line[3:9]
            self.indent=line[9:11]
            self.subclsSeqNum=line[11:15]
            self.nextHigSub=line[15:21]
            self.title=line[21:len(line)+1].strip()[0:140]
            self.clsList.append([self.cls,self.subcls,self.indent,self.subclsSeqNum,self.nextHigSub,self.title])
        reader.close()
        return self.clsList

if __name__=="__main__":
    parser=ClassificationParser()
    filePath=os.getcwd()+"/CLS/ctaf1204.txt"
    lst=parser.GetClasses(filePath)
    import MySQLProcessor
    processor=MySQLProcessor.MySQLProcess()
    processor.connect()
    print len(lst)
    for i in range(0,17):
        if((i+1)*10000<len(lst)):
            processor.executeMany("INSERT INTO uspto_patents.USCLASSIFICATION (Class,Subclass,Indent,SubclsSqsNum,NextHigherSub,Title) VALUES (%s,%s,%s,%s,%s,%s)",lst[i*10000:(i+1)*10000])
        else:
            processor.executeMany("INSERT INTO uspto_patents.USCLASSIFICATION (Class,Subclass,Indent,SubclsSqsNum,NextHigherSub,Title) VALUES (%s,%s,%s,%s,%s,%s)",lst[i*10000:len(lst)+1])
        print '{0}*10000 records have been inserted into the table [USCLASSIFICATION] successfully!'.format(i+1)
    processor.close()
    print '**********\nCongratulations!{0} records have been inserted into the database successfully!\n**********'.format(len(lst))
    text=raw_input('Press ENTER to continue')


