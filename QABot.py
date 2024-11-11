from abc import ABC, abstractmethod
import datetime
import time
import os 
import sys
import QA_Bot_Helper

DICOMFolder = "/Users/mri/Documents/QA/ClinicalQA/RawDICOM"
class QABot:
    def __init__(self):
        self.QAObjects = []
        self.IterationTime = 10
        self.DownloadSafeTime = 1

    def RegisterQA(self,QAObj):
        #Function where you pass a QAObject to register it 
        self.QAObjects.append(QAObj)

    def RunBot(self):
        #Iterate over all QA Objects calling the method which checks for any releavent files, this method will then return the file(s) that are releavent 
        #If a file is found call the function in QA object that runs the script 
        #After the file has be ran call the QA Objects function to do whatever you want with the results 
        #We will have two versionfo the QA Bot one that runs from a streamlit interface and one that is just command line
        
        while True:
            print ("QA Bot Still alive at " + str(datetime.datetime.now()))
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
    
    def ShowError(self,e,CustomMessage,QAObj):
        print("         Error: " + CustomMessage)
        ErrorMessage=e
        import traceback
        traceback.print_exc()
        TEXT=""
        TEXT+= QAObj.QAName() + " was not able to be processed, this may be due to a set up error \n\n"
        TEXT+="Error:\n"

        TEXT+=str(e)+"\n\n"
        subject = 'Subject: {}\n\n{}'.format(QAObj.QAName() +" QA: UNSUCCESSFUL", TEXT)
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