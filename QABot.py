from abc import ABC, abstractmethod
import datetime
import time
import os 
import sys
import QA_Bot_Helper
import glob
from pathlib import Path
from enum import Enum
import pydicom
import csv

#These global variables are the settings, it could probably be done alot better
DICOMFolder = "/Users/mri/Documents/QA/ClinicalQA/RawDICOM"
SendEmails=True
UpdateGoogleSheet=True
GoogleSheetJSON = "qaproject-441416-f5fec0c61099.json"
WorkbookName = "QA Record"
BackUpTime=24
ArchivePath = "Archive"

class QABotState(Enum):
    Idle=1
    FindingFiles=2
    Analysis=3
    Reporting=4
    Cleanup=5

class QABot:
    def __init__(self):
        self.QAObjects = []
        self.IterationTime = 10
        self.DownloadSafeTime = 30
        self.BackupTimer = 0
        self.KeepRunning=True
        self.CurrentlyRunning=False
        self.__Status = QABotState.Idle
        self.CheckDICOMForName = True
        
        if not os.path.exists(ArchivePath):
            os.makedirs(ArchivePath)
    
    def GetStatus(self):
        return self.__Status

    def RegisterQA(self,QAObj):
        #Function where you pass a QAObject to register it 
        self.QAObjects.append(QAObj)

    def CheckDICOMHasRealName(self,filesDict):
        if "folder" not in filesDict:
            raise Exception("No folder found in the filesDict")
        folder = filesDict["folder"]
        file = glob.glob( os.path.join( folder,"*.dcm"))[0]
        LoadedDICOM = pydicom.read_file( file )
        FirstName = LoadedDICOM[0x10,0x0010].value.given_name
        Surname = LoadedDICOM[0x10,0x0010].value.family_name

        FirstNameFile = open(os.path.join("NameDatabase","FirstNames.csv"), 'r')
        reader = csv.reader(FirstNameFile)
        for row_number, row in enumerate(reader, start=1):
            if FirstName == row[2]:
                raise Exception("First name in DICOM was found in the database, please check the file")
        
        SurNameFile = open(os.path.join("NameDatabase","SurNames.csv"), 'r')
        reader = csv.reader(SurNameFile)
        for row_number, row in enumerate(reader, start=1):
            if Surname == row[2]:
                raise Exception("Surname in DICOM was found in the database, please check the file")
                

    def RunBot(self):
        #Iterate over all QA Objects calling the method which checks for any releavent files, this method will then return the file(s) that are releavent 
        #If a file is found call the function in QA object that runs the script 
        #After the file has be ran call the QA Objects function to do whatever you want with the results 
        #We will have two versionfo the QA Bot one that runs from a streamlit interface and one that is just command line
        self.CurrentlyRunning=True
        while self.KeepRunning:
            print ("QA Bot Still alive at " + str(datetime.datetime.now()))
            filesDict = None
            self.__Status = QABotState.Idle #Reset it back to idle each time...
            ResultDict=None
            for QAObj in self.QAObjects:
                try:
                    self.__Status = QABotState.FindingFiles
                    filesDict = QAObj.FindFiles()
                    self.__Status = QABotState.Idle
                except Exception as e:
                    self.ShowError(e,"Find Files",QAObj)
            
                if filesDict != None:
                    print("Running QA : " + QAObj.QAName())
                    time.sleep(self.DownloadSafeTime) #Wait 30s to make sure it really is downaloded...
                    try:
                        self.__Status = QABotState.Analysis
                        ResultDict = QAObj.RunAnalysis(filesDict)
                    except Exception as e:
                        self.ShowError(e,"Run Analysis",QAObj)

                    try:
                        self.__Status = QABotState.Reporting
                        if self.CheckDICOMForName == True:
                            self.CheckDICOMHasRealName(filesDict)
                        QAObj.ReportData(filesDict,ResultDict)
                    except Exception as e:
                        self.ShowError(e,"Report Data",QAObj)

                    try:
                        self.__Status = QABotState.Cleanup
                        QAObj.CleanUpFiles(filesDict,ResultDict)
                    except Exception as e:
                        self.ShowError(e,"Clean Up Files",QAObj)

                self.__Status = QABotState.Idle

                try:
                    DoBackUp=False
                    if not os.path.exists("Sheets_Backup"):
                        DoBackUp=True
                    else:
                        files = glob.glob(os.path.join("Sheets_Backup",'*.csv'))
                        if len(files) == 0:
                            DoBackUp=True
                        else:
                            dates = []
                            for file in files:
                                date = file.split()[2].split("-")
                                dates.append( datetime.datetime( int(date[0]), int(date[1]), int(date[2])) )
                            dates = sorted(dates)
                            latestdate = dates[-1]
                            if datetime.datetime.now() > latestdate+datetime.timedelta(days=1):
                                DoBackUp=True
                    
                    if DoBackUp==True:
                        QA_Bot_Helper.BackUpGoogleSheet()
                except Exception as e:

                    TEXT=""
                    TEXT+= "An error occured during the google sheet backup process \n\n"
                    TEXT+="Error:\n"
                    TEXT+=str(e)+"\n\n"
                    subject = "QABot: Google sheets back up error"
                    QA_Bot_Helper.SendEmail(TEXT,subject)
                    
            time.sleep(self.IterationTime)
        self.CurrentlyRunning=False
        print ("QA Bot Succesfully Stopped")

    
    def ShowError(self,e,CustomMessage,QAObj):
        print("         Error: " + CustomMessage)
        ErrorMessage=e
        import traceback
        traceback.print_exc()
        
        TEXT=""
        TEXT+= QAObj.QAName() + " caused an error during processing, the error is displayed below \n\n"
        TEXT+="Error:\n"

        TEXT+=str(e)+"\n\n"
        subject = QAObj.QAName() +": ERROR"

        Path('ErrorLog.txt').touch(exist_ok=True)
        f = open("ErrorLog.txt", "a")
        f.write("Error logged at " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") +"\n")
        f.write(traceback.format_exc())
        f.write("\n\n")

        QA_Bot_Helper.SendEmail(TEXT,subject)
        pass      


#Each QA should be made into a QA object and added to the QAbot
class QAObject(ABC):
    def __init__(self):
        pass

    #If files matching what you want are found then return a dict of files
    @abstractmethod
    def FindFiles(self) -> dict:
        pass

    #Take the files and run analysis on them
    @abstractmethod
    def RunAnalysis(self, files)->dict:
        pass

    #Report the data whoever we want to
    @abstractmethod
    def ReportData(self,files,ResultDict):
        pass
    
    #Do whatever we need to wrap up with like archive the DICOM
    @abstractmethod
    def CleanUpFiles(self,files,ResultDict):
        pass

    # Way to get the name of the QA
    @abstractmethod
    def QAName(self):
        pass
    
    #Run the unit tests
    @abstractmethod
    def RunUnitTest(self,path):
        pass