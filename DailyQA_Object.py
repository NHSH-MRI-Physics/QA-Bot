import datetime
import QABot
import os
import sys
sys.path.insert(0, 'DailyQA\DailyQA-main\DQA_Scripts')
import DailyQA
import shutil
import Helper
import QA_Bot_Helper
import numpy as np
import glob

class DailyQAObj(QABot.QAObject):
    def __init__(self):
        self.QASuccess = False
        self.QAResult = []
        self.ArchiveFolder=None

    def RunAnalysis(self, files):
        print("Running: " + files["QAName"])
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
        
    
    def ReportData(self, files, ResultDict):
        #TODO Check if QA passed then record result in the Google spreadsheet and send the email out
        QAName = files["QAName"]
        if self.QASuccess == True:
            Results = ResultDict["Results"]
            OverallPass = False
            OverallPass=[]
            EmailResultLines = []
            images = []
            for result in Results:
                QAResult = Helper.DidQAPassV2(result)
                self.QAResult.append(QAResult)
                OverallPass.append(QAResult[0])
                EmailResultLines.append(QAResult[1])
                images.append(os.path.join("DailyQA","DailyQA-main","Results",result[-1]+"_SmoothMethod.png"))
        
            TEXT = ""
            if False in OverallPass:
                TEXT+="Daily " + QAName + " QA Results run on " + str(datetime.date.today()) + "    Result: Fail\n\n"
                subject = "Daily " + QAName +" QA: FAIL"
            else:
                TEXT+="Daily " + QAName + " QA Results run on " + str(datetime.date.today()) + "    Result: Pass\n\n"
                subject = "Daily " + QAName +" QA: PASS"

            for line in EmailResultLines:
                TEXT+=line +  "\n"

            self.ArchiveFolder = os.path.join("Archive","DailyQA_"+QAName+"_"+str(datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")))
            self.ArchiveFolder = self.ArchiveFolder.replace("Users", QAName)

            NumberOfFilesLastRun = int(np.load("temp.npy"))
            TimePerImage = 0.028
            QA_Bot_Helper.UpdateTotalManHours(TimePerImage*NumberOfFilesLastRun)
            TEXT+="Estimated Total Man Hours Saved: " + str( round(QA_Bot_Helper.GetTotalManHoursSaved(),2)) + " hours\n\n"
            TEXT+= "Archive Folder: "+self.ArchiveFolder + "\n"
            QA_Bot_Helper.SendEmail(TEXT,subject,images)


    def CleanUpFiles(self, files, ResultDict):
        #Archive all the files
        folder = files["folder"]
        QAName = files["QAName"]
        Results = ResultDict["Results"]


        #Move to the archive 
        os.system("echo ilovege | sudo -S chown mri "+folder)
        os.rename(folder, self.ArchiveFolder)
        if (self.QASuccess==True):
            for result in Results:
                shutil.copyfile(os.path.join("DailyQA","DailyQA-main","Results",result[-1]+"_SmoothMethod.png"), os.path.join(self.ArchiveFolder,result[-1]+"_SmoothMethod.png"))

        #Delete all the images in the results folder
        images = glob.glob(os.path.join("DailyQA","DailyQA-main","Results","*.png"))
        for image in images:
            os.remove(image)

    def QAName(self):
        return "Daily QA"
    