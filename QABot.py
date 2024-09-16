from abc import ABC, abstractmethod
import datetime
import time
import os 

class QABot:
    QAObjects = []
    IterationTime = 10
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
                filesDict = QAObj.FindFiles()
                if filesDict != None:
                    ReturnDict = QAObj.RunAnalysis(filesDict)
                    QAObj.ReportData(ReturnDict)
                    QAObj.CleanUpFiles(filesDict)
            time.sleep(self.IterationTime)



class QAObject(ABC):
    
    def __init__(self):
        pass

    @abstractmethod
    def FindFiles(self) -> dict:
        pass

    @abstractmethod
    def RunAnalysis(self, files)->dict:
        pass

    @abstractmethod
    def ReportData(self,ResultDict):
        pass
    
    @abstractmethod
    def CleanUpFiles(self,files):
        pass

    @abstractmethod
    def QAName(self):
        pass