from abc import ABC, abstractmethod
import datetime
import time
import os 
DICOMFolder = "/Users/mri/Documents/QA/ClinicalQA/RawDICOM"
class QABot:

    def __init__(self):
        self.QAObjects = []
        self.IterationTime = 10
        

    def RegisterQA(self,QAObj):
        #Function where you pass a QAObject to register it 
        self.QAObjects.append(QAObj)

    def RunBot(self):
        #Iterate over all QA Objects calling the method which checks for any releavent files, this method will then return the file(s) that are releavent 
        #If a file is found call the function in QA object that runs the script 
        #After the file has be ran call the QA Objects function to do whatever you want with the results 
        #We will have two versionfo the QA Bot one that runs from a streamlit interface and one that is just command line
        
        while True:
            try:
                print ("QA Bot Still alive at " + str(datetime.datetime.now()))
                for QAObj in self.QAObjects:
                    filesDict = QAObj.FindFiles()
                    if filesDict != None:
                        print("Running QA : " + QAObj.QAName())
                        ResultDict = QAObj.RunAnalysis(filesDict)
                        QAObj.ReportData(ResultDict)
                        QAObj.CleanUpFiles(filesDict,ResultDict)
                time.sleep(self.IterationTime)
            except Exception as e:
                    print (str(e))
                    #TODO Make this exceptuon show line and file that it came from...

                    ErrorMessage=e
                    #Send out error email
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
    def ReportData(self,ResultDict):
        pass
    
    #Do whatever we need to wrap up with like archive the DICOM
    @abstractmethod
    def CleanUpFiles(self,files,ResultDict):
        pass

    # Way to get the name of the QA
    @abstractmethod
    def QAName(self):
        pass