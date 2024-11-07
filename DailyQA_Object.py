import datetime
import QABot
import os
import sys
sys.path.insert(0, 'DailyQA\DailyQA-main\DQA_Scripts')
import DailyQA
import shutil
import Helper

class DailyQAObj(QABot.QAObject):
    def __init__(self):
        self.QASuccess = False

    def RunAnalysis(self, files):
        Results = DailyQA.RunDailyQA(files["folder"])
        self.QASuccess = True
        return {"Results": Results}

    def FindFiles(self):
        FileCount =  {}
        FileCount["DQA_Head"] = 19
        FileCount["DQA_Body"] = 50
        FileCount["DQA_Spine"] = 48
        SubFolders = [x[0] for x in os.walk(QABot.DICOMFolder)]
        for folder in SubFolders:
            for QAName in FileCount.keys():
                if QAName.lower() in folder.lower():
                    FileCounter = len(os.listdir(folder))
                    if (FileCounter >= FileCount[QAName]):
                        return {"folder":folder, "QAName":QAName}
        
    
    def ReportData(self, ResultDict):
        #TODO Check if QA passed then record result in the Google spreadsheet and send the email out
        Results = ResultDict["Results"]
        for result in Results:
            QAResult = Helper.DidQAPassV2(result)
            x = 0

    def CleanUpFiles(self, files, ResultDict):
        folder = files["folder"]
        QAName = files["QAName"]
        Results = ResultDict["Results"]

        NewFolder = os.path.join("Archive","DailyQA_"+QAName+"_"+str(datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")))
        NewFolder = NewFolder.replace("Users", QAName)
        #Move to the archive 
        images = []
        os.system("echo ilovege | sudo -S chown mri "+folder)
        os.rename(folder, NewFolder)
        if (self.QASuccess==True):
            for result in Results:
                shutil.copyfile(os.path.join("DailyQA","DailyQA-main","Results",result[-1]+"_SmoothMethod.png"), os.path.join(NewFolder,result[-1]+"_SmoothMethod.png"))
                images.append(os.path.join(NewFolder,result[-1]+"_SmoothMethod.png"))
        #TODO IF qa is not succesfull send out an error email 

    def QAName(self):
        return "Daily QA"
    