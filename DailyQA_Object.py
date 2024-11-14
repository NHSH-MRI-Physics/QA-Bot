import datetime
import QABot
import os
import sys
sys.path.insert(0, os.path.join('DailyQA','DailyQA-main','DQA_Scripts'))
import DailyQA
import shutil
import Helper
import QA_Bot_Helper
import numpy as np
import glob
import pydicom
import gspread

class DailyQAObj(QABot.QAObject):
    def __init__(self):
        self.QASuccess = False
        self.QAResult = []
        self.ArchiveFolder=None
        self.scanername = None
        self.date=None
        self.overallpass = []
        self.SNRResult=None

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
                        file = glob.glob( os.path.join( folder,"*.dcm"))[0]
                        LoadedDICOM = pydicom.read_file( file )
                        self.scanername =LoadedDICOM[0x08,0x80].value.split(" ")[-2]  + " " + LoadedDICOM[0x08,0x80].value.split(" ")[-1]
                        return {"folder":folder, "QAName":QAName}


    def RunAnalysis(self, files):
        print("Running: " + files["QAName"])
        Results = DailyQA.RunDailyQA(files["folder"])
        self.QASuccess = True
        return {"Results": Results}        
    
    def ReportData(self, files, ResultDict):
        QAName = files["QAName"]
        if self.QASuccess == True:
            Results = ResultDict["Results"]
            self.SNRResult = Results
            OverallPass = False
            OverallPass=[]
            EmailResultLines = []
            images = []
            self.QAResult = []
            for result in Results:
                QAResult = Helper.DidQAPassV2(result)
                self.QAResult.append(QAResult)
                OverallPass.append(QAResult[0])
                EmailResultLines.append(QAResult[1])
                images.append(os.path.join("DailyQA","DailyQA-main","Results",result[-1]+"_SmoothMethod.png"))
            self.overallpass = OverallPass
            self.date = datetime.datetime.now()
        
            TEXT = ""
            if False in OverallPass:
                TEXT+="Daily " + QAName + " QA Results run on " + self.scanername + " at " + str(self.date) + "    Result: Fail\n\n"
                subject = self.scanername + " Daily " + QAName +" QA: FAIL"
            else:
                TEXT+="Daily " + QAName + " QA Results run on "+ self.scanername + " at " + str(self.date) + "    Result: Pass\n\n"
                subject = self.scanername +  " Daily " + QAName +" QA: PASS"

            for line in EmailResultLines:
                TEXT+=line +  "\n"


            self.ArchiveFolder = os.path.join("Archive","DailyQA_"+QAName+"_"+str(self.date.strftime("%Y-%m-%d %H-%M-%S")))
            self.ArchiveFolder = self.ArchiveFolder.replace("Users", QAName)

            NumberOfFilesLastRun = int(np.load("temp.npy"))
            TimePerImage = 0.028
            QA_Bot_Helper.UpdateTotalManHours(TimePerImage*NumberOfFilesLastRun)
            TEXT+="Estimated Total Man Hours Saved: " + str( round(QA_Bot_Helper.GetTotalManHoursSaved(),2)) + " hours\n\n"
            TEXT+= "Archive Folder: "+self.ArchiveFolder + "\n"
            QA_Bot_Helper.SendEmail(TEXT,subject,images)

            #Fill out spreadsheet
            gc = gspread.service_account(filename="qaproject-441416-f5fec0c61099.json")
            sh = gc.open("QA Record")


            for i in range(len(self.QAResult)):
                values_list = sh.worksheet("DailyQA").col_values(1)
                LastRow = len(values_list)+1
                Values = []
                Values.append(str(self.date.strftime("%Y-%m-%d %H-%M-%S")))
                Values.append(QAName)
                if self.QAResult[i][0] == True:
                    Values.append("Pass")
                else:
                    Values.append("Fail")
                Values.append(self.scanername)
                Values.append(self.ArchiveFolder)
                Values.append(self.SNRResult[i][3])
                Values.append(self.SNRResult[i][0])
                
                ROIS = ["M1","M2","M3","M4","M5"]
                for j in range(5): 
                    for k in range(len(self.SNRResult[i][1]["M1"])):
                        Values.append(self.SNRResult[i][1][ROIS[j]][k])
                sh.worksheet("DailyQA").update( [Values],"A"+str(LastRow))

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
    