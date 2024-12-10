from abc import ABC, abstractmethod
import datetime
import time
import os 
import sys
import QA_Bot_Helper
import glob
from pathlib import Path

#These global variables are the settings, it could probably be done alot better
DICOMFolder = "/Users/mri/Documents/QA/ClinicalQA/RawDICOM"
SendEmails=True
UpdateGoogleSheet=True
GoogleSheetJSON = "qaproject-441416-f5fec0c61099.json"
WorkbookName = "QA Record"
BackUpTime=24

class QABot:
    def __init__(self):
        self.QAObjects = []
        self.IterationTime = 10
        self.DownloadSafeTime = 1
        self.BackupTimer = 0
        self.running=True

        if not os.path.exists("Archive"):
            os.makedirs("Archive")

    def RegisterQA(self,QAObj):
        #Function where you pass a QAObject to register it 
        self.QAObjects.append(QAObj)

    def RunBot(self):
        #Iterate over all QA Objects calling the method which checks for any releavent files, this method will then return the file(s) that are releavent 
        #If a file is found call the function in QA object that runs the script 
        #After the file has be ran call the QA Objects function to do whatever you want with the results 
        #We will have two versionfo the QA Bot one that runs from a streamlit interface and one that is just command line

        while self.running:
            print ("QA Bot Still alive at " + str(datetime.datetime.now()))
            filesDict = None
            for QAObj in self.QAObjects:
                try:
                    filesDict = QAObj.FindFiles()
                except Exception as e:
                    self.ShowError(e,"Find Files",QAObj)
            
                if filesDict != None:
                    print("Running QA : " + QAObj.QAName())
                    time.sleep(self.DownloadSafeTime) #Wait 30s to make sure it really is downaloded...
                    try:
                        ResultDict = QAObj.RunAnalysis(filesDict)
                    except Exception as e:
                        self.ShowError(e,"Run Analysis",QAObj)

                    try:
                        QAObj.ReportData(filesDict,ResultDict)
                    except Exception as e:
                        self.ShowError(e,"Report Data",QAObj)

                    try:
                        QAObj.CleanUpFiles(filesDict,ResultDict)
                    except Exception as e:
                        self.ShowError(e,"Clean Up Files",QAObj)
                
                time.sleep(self.IterationTime)

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